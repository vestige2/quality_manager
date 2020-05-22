from django.db import models

from team_management.core.base_memebers.models import TeamMember


class IssueType(models.Model):
    name = models.CharField(
        'Наименование',
        max_length=400,
        null=True
    )
    uid = models.CharField(
        'id в Jira',
        max_length=400,
        null=True
    )

    class Meta:
        db_table = 'jira_issuetype'


class Issue(models.Model):
    uid = models.CharField(
        'id задачи в системе',
        max_length=200,
        null=True
    )

    verbose_key = models.CharField(
        'Нормальное название задачи',
        max_length=200,
        null=True
    )

    type = models.ForeignKey(
        to=IssueType,
        verbose_name='Ссылка на тип',
        on_delete=models.PROTECT,
        null=True
    )

    original_estimate = models.IntegerField(
        'Первоначальная оценка',
        null=False,
        default=0
    )

    class Meta:
        db_table = 'jira_issue'


class JiraUser(models.Model):

    user = models.ForeignKey(
        to=TeamMember,
        verbose_name='Ссылка на тиммембера',
        on_delete=models.PROTECT,
        null=True
    )

    jira_login = models.CharField(
        'логин в jira',
        max_length=200,
        null=True
    )

    class Meta:
        db_table = 'jira_user'


class WorklogType(models.Model):
    name = models.CharField(
        'Наименование типа списания',
        max_length=255,
        null=True
    )

    class Meta:
        db_table = 'jira_worklogtype'


class WorkLog(models.Model):
    uid = models.CharField(
        'Уид списания',
        max_length=255,
        null=True
    )

    logged_time = models.IntegerField(
        'Затраченное время в секундах',
        null=True
    )

    date = models.DateField(
        'Когда залогировано время',
        null=True
    )

    issue = models.ForeignKey(
        to=Issue,
        verbose_name='Ссылка на задачу',
        on_delete=models.PROTECT,
        null=True
    )

    jira_user = models.ForeignKey(
        to=JiraUser,
        verbose_name='Ссылка на jira_user',
        on_delete=models.PROTECT,
        null=True
    )

    worklog_type = models.ForeignKey(
        to=WorklogType,
        verbose_name='Тип списания',
        on_delete=models.PROTECT,
        null=True
    )

    class Meta:
        db_table = 'jira_worklog'


class LoadingJiraInformation(models.Model):
    data_type = models.IntegerField(
        'Тип данных',
        null=True
    )
    date = models.DateField(
        'Когда началась загрузка',
        null=True
    )

    jql = models.CharField(
        'JQL запроса',
        max_length=255,
        null=True
    )

    data_count = models.IntegerField(
        'Сколько было загружено данных по JQL',
        null=True
    )

    class Meta:
        db_table = 'jira_loading_information'


