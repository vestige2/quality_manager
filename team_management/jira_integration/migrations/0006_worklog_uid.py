# Generated by Django 2.2.3 on 2019-09-04 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira_integration', '0005_auto_20190904_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='worklog',
            name='uid',
            field=models.CharField(max_length=255, null=True, verbose_name='Уид списания'),
        ),
    ]
