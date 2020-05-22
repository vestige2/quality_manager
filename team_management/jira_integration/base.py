import datetime
import logging
from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Max
from jira.client import JIRA, translate_resource_args
from jira.utils import json_loads, CaseInsensitiveDict

from team_management.core.base_memebers.models import TeamMember
from team_management.jira_integration.models import (
    JiraUser, IssueType, Issue, WorkLog, WorklogType)


# https://jira.bars.group/rest/tempo-timesheets/3/worklogs/2934641


class JiraWorklogType:
    """Worklogtype on an issue."""

    JIRA_BASE_URL = '{server}/rest/{path}'

    def __init__(self, options, session, base_url=JIRA_BASE_URL):
        self._resource = 'tempo-timesheets/3/worklogs/{0}'
        self._options = options
        self._session = session
        self._base_url = base_url

        # Explicitly define as None so we know when a resource has actually
        # been loaded
        self.raw = None

    def find(self, id, params=None):
        path = self._resource.format(*id)

        url = self._get_url(path)
        self._load(url)

    def _get_url(self, path):
        options = self._options.copy()
        options.update({'path': path})
        return self._base_url.format(**options)

    def _load(self, url, headers=CaseInsensitiveDict(), params=None, path=None):
        r = self._session.get(url, headers=headers, params=params)
        try:
            j = json_loads(r)
        except ValueError as e:
            logging.error("%s:\n%s" % (e, r.text))
            raise e
        if path:
            j = j[path]
        try:
            self.w_type = j['worklogAttributes'][0]['value']
        except (IndexError, KeyError):
            self.w_type = ''


class BaseJira(JIRA):

    @translate_resource_args
    def worklog_type(self, id, params=None):
        """Get a specific worklog Resource from the server.

        :param issue: ID or key of the issue to get the worklog from
        :param id: ID of the worklog to get
        """
        return self._find_for_resource(JiraWorklogType, (id,), params)


class JiraConnection:
    login = 'a.morozov'
    password = 'y6XphtVv'

    jira_options = {'server': 'https://jira.bars.group'}

    @classmethod
    def connect(cls):
        jira = BaseJira(options=cls.jira_options, basic_auth=(cls.login, cls.password))
        return jira


class JQLFilterTasks:
    def __init__(self, jira, jql, start, max_results=1000):
        self.jql = jql
        self.jira = jira
        self.start = start
        self.max_results = max_results

    @property
    def issues_list(self):
        return self.jira.search_issues(
                self.jql,
                startAt=self.start,
                maxResults=self.max_results)

    @property
    def get_total(self):
        return self.jira.search_issues(
                self.jql,
                startAt=self.start,
                maxResults=10).total


class InitialFilling:

    def __init__(self):
        self.jira = JiraConnection().connect()

    @transaction.atomic
    def run(self):
        jira = self.jira
        # jql = 'project = BOZIK AND issuetype in (Bug, Improvement, "New Feature", Task, Инцидент) AND updated >= startOfMonth(-1)'
        jql = 'project = BOZIK AND issuetype in (Bug, Improvement, "New Feature", Task, Инцидент)'
        start = 0
        total = 0
        max = JQLFilterTasks(jira, jql, start).get_total
        wt_cache = {}
        tm_users_cache = {}
        jira_users_cache = {}
        task_types_cache = {}
        tasks_cache = defaultdict()
        while total < max:
            issues = JQLFilterTasks(jira, jql, start).issues_list
            to_create_users = defaultdict()
            to_create_tasks = defaultdict()
            to_create_wlogs = defaultdict(list)
            to_create_issue_types = defaultdict()
            for n, issue in enumerate(issues, start=1):
                print(f"Начало обработки загруженных данных {datetime.datetime.now().strftime('%H:%M:%S')}")
                # типы задач
                it_name = issue.fields.issuetype.name
                it_uid = issue.fields.issuetype.id
                to_create_issue_types[it_name] = it_uid
                # задачи
                i_uid = issue.id
                i_verbose_key = issue.key
                i_type_name = issue.fields.issuetype.name
                i_estim = 0
                if issue.fields.aggregatetimeoriginalestimate:
                   i_estim = issue.fields.aggregatetimeoriginalestimate
                to_create_tasks[i_uid] = (i_verbose_key, i_type_name, i_estim)
                worklogs = jira.worklogs(issue)
                for worklog in worklogs:
                    # юзеры
                    wlt = self.jira.worklog_type(worklog.id)
                    if not wt_cache.get(wlt.w_type):
                        wlt_type, _ = WorklogType.objects.get_or_create(
                            name=wlt.w_type)
                        wt_cache[wlt.w_type] = wlt_type.id
                    user_name = worklog.author.displayName
                    user_jira_login = worklog.author.name
                    to_create_users[user_jira_login] = user_name
                    # ворклоги
                    w_issue = worklog.issueId
                    w_logged_time = worklog.timeSpentSeconds
                    w_date = worklog.updated
                    w_jira_user = worklog.author.name
                    to_create_wlogs[w_jira_user].append((w_issue, w_logged_time, w_date, wt_cache[wlt.w_type], worklog.id))
            print(
                f"Начало обработки юзеров {datetime.datetime.now().strftime('%H:%M:%S')}")
            for key, val in to_create_users.items():
                if not tm_users_cache.get(val):
                    tm, created = TeamMember.objects.get_or_create(
                        iname=val
                    )
                    tm_users_cache[val] = tm.id
                if not jira_users_cache.get(key):
                    ju, created = JiraUser.objects.get_or_create(
                        user_id=tm_users_cache[val],
                        jira_login=key)
                    jira_users_cache[key] = ju.id
            print(
                f"Начало обработки типов задач {datetime.datetime.now().strftime('%H:%M:%S')}"
            )
            for it, vals in to_create_issue_types.items():
                if not task_types_cache.get(it):
                    _it, _ = IssueType.objects.get_or_create(
                        name=it,
                        uid=vals
                    )
                    task_types_cache[it] = _it.id
            print(
                f"Начало обработки типов задач {datetime.datetime.now().strftime('%H:%M:%S')}"
            )
            for _t_uid, (_k, _t_n, _i_e) in to_create_tasks.items():
                _i, _ = Issue.objects.get_or_create(
                    uid=_t_uid,
                    verbose_key=_k
                )
                _i.type_id = task_types_cache.get(_t_n)
                _i.original_estimate = _i_e
                _i.save()
                tasks_cache[_t_uid] = _i.id

            print(
                f"Начало обработки ворклогов {datetime.datetime.now().strftime('%H:%M:%S')}"
            )
            for _w_u, l_vals in to_create_wlogs.items():
                u = jira_users_cache.get(_w_u)
                for (_i, _lt, _d, _wtt, _wuid) in l_vals:
                    issue = tasks_cache.get(_i)
                    w = WorkLog.objects.filter(
                        uid=_wuid,
                    ).first()
                    if not w:
                        w = WorkLog(uid=_wuid)
                    w.logged_time = _lt or 0
                    w.date = _str2date_or_datetime(_d)
                    w.issue_id = issue
                    w.jira_user_id = u
                    w.worklog_type_id = _wtt
                    w.save()
            start += 1000
            total += len(issues)
            print(f'{total} из {max}')

    def create_task_original_estimate(self):
        # wlogs = Worklog.objects.all()
        # for w in wlogs:
        #     wlt = self.jira.worklog_type(w.id)
        #     wlt_type, _ = WorklogType.objects.get_or_create(
        #         name=wlt.w_type)
        #     w.worklog_type_id = wlt_type.id
        #     w.save()
        pass

# jira.issue(issues_list[0]).fields.issuetype
# jira.worklogs(issues_list[0])


def _str2date_or_datetime(
        raw_value, as_date=True):
    """
    Преобразует строку к дате или дате со временем
    :param raw_value: изначальная строка
    :param value_format: формат строки
    :param err_value: значение, возвращаемое в случае ошибки преобразования
    :param do_raise: вызывать исключение в случае ошибки преобразования
    :param as_date: возвращать значение, как дату
    """
    result = None
    if isinstance(raw_value, datetime.date):
        result = raw_value
    else:
        datetime_templates = (
            ('%d.%m.%Y', 10),
            ('%Y-%m-%dT%H:%M:%S', 19),
            ('%Y-%m-%d %H:%M:%S', 19),
            ('%d.%m.%Y %H:%M:%S', 19),
            ('%Y-%m-%dT%H:%M', 16),
            ('%Y-%m-%d %H:%M', 16),
            ('%d.%m.%Y %H:%M', 16),
            ('%Y-%m-%d', 10),
            ('%H:%M:%S', 8),
            ('%H:%M', 5),
        )

        for tmpl, baund in datetime_templates:
            try:
                curr_date = datetime.datetime.strptime(
                    raw_value[:baund], tmpl
                )
                if as_date:
                    curr_date = curr_date.date()
            except (ValueError, TypeError) as err:
                pass
            else:
                result = curr_date
                break

    return result


class Report:

    def run(self):
        """
        [
        {(юзер, месяц): [(worked_task, ср.коэффициент) . . .]},
        ...
        {(юзер, месяц): [(worked_task, ср.коэффициент). . .]},
        ]
        """
        result = []
        users = dict(JiraUser.objects.values_list(
            'pk', 'jira_login'
        ).distinct())
        for user, login in users.items():
            row = defaultdict(list)
            master_q = WorkLog.objects.filter(
                jira_user_id=user,
                worklog_type__in=[22, 28]
            )
            if master_q.exists():
                tasks_plan_time = master_q.values(
                    'issue__verbose_key',
                    'issue__original_estimate',
                    ).annotate(fact_time=Sum('logged_time'))

                tasks_info_dicts = defaultdict(list)
                for t in tasks_plan_time:
                    tasks_info_dicts[t['issue__verbose_key']] = [Decimal(t['issue__original_estimate'] / t['fact_time'])]

                tasks_by_dates = master_q.values(
                    'issue__verbose_key'
                ).annotate(max_date=Max('date'))

                for t in tasks_by_dates:
                    tasks_info_dicts[t['issue__verbose_key']].append(t['max_date'].strftime('%B %Y'))

                for key, value in tasks_info_dicts.items():
                    row[(login, value[1])].append((key, value[0]))

                result.append(row)
                # print(row)
        print_row = ''
        for r in result:
            for key, val in r.items():
                print_row = f'{key[0]}|{key[1]}|{len(val)}|{sum([v[1] for v in val])/len(val)}|'
                print(print_row)
