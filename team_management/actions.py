from django import shortcuts
from m3 import OperationResult
from m3.actions import ActionPack, Action

from team_management.jira_integration.base import InitialFilling, Report
from team_management.jira_integration.part_loader import TaskLoader, \
    WorkLogLoader, WorklogTypeLoader


class MainTMDesktopPack(ActionPack):
    url = '/desktop'
    shortname = url[1:]

    def __init__(self):
        super().__init__()
        self.desktop_action = DesktopAction()
        self.some_ajax = SomeAjax()
        self.actions.append(self.desktop_action)
        self.actions.append(self.some_ajax)


class DesktopAction(Action):
    url = '/show'
    shortname = 'desktop'

    def get_template(self):
        return 'tm_main_templs/index.html'

    def run(self, request, context):

        return shortcuts.render_to_response(
                self.get_template(), context={})


class SomeAjax(Action):
    url = '/some_ajax'
    shortname = 'some_ajax'

    def run(self, request, context):
        # _if = InitialFilling()
        # _if.run()
        # _if.create_task_original_estimate()
        # Report().run()
        # WorkLogLoader().load()
        # WorklogTypeLoader().load()
        Report().run()

        return OperationResult(success=True,
                               message='Не удалось загрузить файл.',
                               code="function (){alert('Все хорошо');}"
                               )
