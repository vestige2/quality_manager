from django.db import models


class Team(models.Model):
    team_name = models.CharField(
        'Наименование команды',
        null=False,
        max_length=200
    )