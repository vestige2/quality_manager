from django import shortcuts
from m3.actions import ActionPack, Action

from team_management.core.teams.models import Team


class TeamPack(ActionPack):
    """
    Управление членами команды
    """
    url = '/teams'
    shortname = url[1:]

    def __init__(self):
        super().__init__()
        self.main = TeamMainAction()
        self.actions.extend([
            self.main,
        ])


class TeamMainAction(Action):
    url = '/show'
    shortname = url[1:]

    def get_template(self):
        return 'teams/index.html'

    def run(self, request, context):
        result = Team.objects.all()

        return shortcuts.render_to_response(
            self.get_template(), context={'all': result})
