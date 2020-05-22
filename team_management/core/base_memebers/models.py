from django.db import models


class Candidate(models.Model):
    iname = models.CharField(
        'ФИО',
        null=False,
        max_length=200
    )

    class Meta:
        abstract = True


class TeamMember(Candidate):

    class Meta:
        db_table = 'tm_team_member'
