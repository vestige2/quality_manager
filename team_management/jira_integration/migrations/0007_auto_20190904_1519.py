# Generated by Django 2.2.3 on 2019-09-04 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira_integration', '0006_worklog_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worklog',
            name='logged_time',
            field=models.IntegerField(null=True, verbose_name='Затраченное время в секундах'),
        ),
    ]
