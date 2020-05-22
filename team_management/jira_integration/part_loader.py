import datetime
import logging
from collections import defaultdict
from decimal import Decimal

import jira
from django.db import transaction
from django.db.models import Sum, Max

from jira.client import JIRA, translate_resource_args
from jira.utils import json_loads, CaseInsensitiveDict

from team_management.core.base_memebers.models import TeamMember
from team_management.jira_integration.base import JiraConnection, \
    JQLFilterTasks
from team_management.jira_integration.models import (
    JiraUser, IssueType, Issue, WorkLog, WorklogType, LoadingJiraInformation)


ALL_TASKS = ('project = BOZIK AND issuetype in '
             '(Bug, Improvement, "New Feature", Task, Инцидент)')
STEP = 100


class BaseLoader:
    def __init__(self, jql=ALL_TASKS, step=STEP, for_update=False):
        self.jira = JiraConnection().connect()
        self.jql = jql
        self.jira_loader = self.get_jira_loader_object
        self.step = step
        self.current = self.get_curent_count
        self.for_update = for_update

    @property
    def get_jira_loader_object(self):
        lji = LoadingJiraInformation.objects.filter(
            jql=self.jql
        ).last()
        if not lji:
            lji = LoadingJiraInformation(
                jql=self.jql,
                data_count=0,
                date=datetime.datetime.now()
            )
            lji.save()
        return lji

    @property
    def get_curent_count(self):
        return self.jira_loader.data_count

    @property
    def get_total_loading(self):
        return JQLFilterTasks(self.jira, self.jql, self.current).get_total

    def update_count(self, count):
        self.jira_loader.data_count = count
        self.jira_loader.save()
        self.current = count

    def load(self):
        raise NotImplementedError


class TaskLoader(BaseLoader):
    def load(self):
        print(
            f"Начало обработки загруженных данных "
            f"{datetime.datetime.now().strftime('%H:%M:%S')}"
        )
        total_loaded = self.current
        max = self.get_total_loading - self.current
        task_types_cache = {}
        while total_loaded < max:
            data = JQLFilterTasks(self.jira, self.jql, self.current,
                                  max_results=self.step)
            issues = data.issues_list
            for issue in issues:
                _i, _ = Issue.objects.get_or_create(
                    uid=issue.id,
                    verbose_key=issue.key
                )

                if not task_types_cache.get(issue.fields.issuetype.name):
                    _it, _ = IssueType.objects.get_or_create(
                        name=issue.fields.issuetype.name,
                        uid=issue.fields.issuetype.id
                    )
                    task_types_cache[issue.fields.issuetype.name] = _it.id

                i_estim = 0
                if issue.fields.aggregatetimeoriginalestimate:
                    i_estim = issue.fields.aggregatetimeoriginalestimate
                _i.type_id = task_types_cache.get(issue.fields.issuetype.name)
                _i.original_estimate = i_estim
                _i.save()
                self.update_count(self.current+1)
                total_loaded += 1
                print(
                    f"Загружено {total_loaded} из {max}"
                )


class WorkLogLoader(BaseLoader):
    def load(self):
        print(
            f"Начало обработки ворклогов "
            f"{datetime.datetime.now().strftime('%H:%M:%S')}"
        )
        WorkLog.objects.filter(issue_id__isnull=True).delete()
        if not self.for_update:
            loaded_tasks = set(
                WorkLog.objects.values_list('issue__uid', flat=True)
            )
            all_tasks = Issue.objects.exclude(
                uid__in=loaded_tasks
            ).only('id', 'uid')
            if not all_tasks.exists():
                print("Все задачи уже обработаны!")
                return None
        else:
            all_tasks = Issue.objects.only('id', 'uid')
        tm_users_cache = {}
        jira_users_cache = {}
        max = all_tasks.count()
        current = 0
        for task in all_tasks:
            with transaction.atomic():
                worklogs = self.jira.worklogs(task.uid)
                to_update_worklogs = []
                for worklog in worklogs:
                    try:
                        name = worklog.author.displayName
                    except:
                        name = worklog.author.name
                    if not tm_users_cache.get(name):
                        tm, created = TeamMember.objects.get_or_create(
                            iname=name
                        )
                        tm_users_cache[name] = tm.id
                    if not jira_users_cache.get(worklog.author.name):
                        ju, created = JiraUser.objects.get_or_create(
                            user_id=tm_users_cache[name],
                            jira_login=worklog.author.name)
                        jira_users_cache[worklog.author.name] = ju.id
                    w = WorkLog.objects.filter(
                        uid=worklog.id,
                    ).first()
                    if not w:
                        w = WorkLog(uid=worklog.id)
                    w.logged_time = worklog.timeSpentSeconds
                    w.date = _str2date_or_datetime(worklog.updated)
                    w.jira_user_id = jira_users_cache[worklog.author.name]
                    w.save()
                    to_update_worklogs.append(w.id)
                WorkLog.objects.filter(id__in=to_update_worklogs).update(
                    issue_id=task.id)
                current += 1
                print(f'Осталось отработать {max - current}')


class WorklogTypeLoader(BaseLoader):
    def load(self):
        print(
            f"Начало обработки типов ворклогов "
            f"{datetime.datetime.now().strftime('%H:%M:%S')}"
        )
        wlts = WorkLog.objects.filter(worklog_type__isnull=True)
        wt_cache = {}
        current = 0
        max = wlts.count()
        for w in wlts.iterator():
            try:
                wlt = self.jira.worklog_type(w.uid)
            except:
                continue
            if not wt_cache.get(wlt.w_type):
                wlt_type, _ = WorklogType.objects.get_or_create(
                    name=wlt.w_type)
                wt_cache[wlt.w_type] = wlt_type.id
            w.worklog_type_id = wt_cache[wlt.w_type]
            w.save()
            current += 1
            print(f'Осталось отработать {max - current}')



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


