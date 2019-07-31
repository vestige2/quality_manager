from django import template
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import models as auth_models
from django.shortcuts import render_to_response
from django.urls import reverse
from m3 import OperationResult
from m3.actions import ActionPack, Action
from m3.actions.urls import get_url
from m3_ext.ui.results import ExtUIScriptResult


class MainTMDesktopPack(ActionPack):
    url = '/desktop'
    shortname = url[1:]

    def __init__(self):
        super().__init__()
        self.desktop_action = DesktopAction()
        self.actions.append(self.desktop_action)


class DesktopAction(Action):
    url = '/show'
    shortname = 'desktop'

    @staticmethod
    def get_template():
        """
        :return: файл шаблона рабочего стола
        :rtype: str
        """
        return settings.DESKTOP_HTML

    def run(self, request, context):
        from m3_ext.ui.windows.base import BaseExtWindow
        # try:
        #     user = auth_models.User.objects.get(username=request.user)
        #     profile_id = user.userprofile.id
        # except auth_models.User.DoesNotExist:
        #     profile_id = 0
        # params = {'url': get_url(self.url), 'user_id': profile_id,
        #           'username': request.user, 'fname': '', 'iname': '',
        #           'oname': '', 'email': '', 'DEBUG': settings.DEBUG,
        #           'title': 'некий титл'}
        #
        # return render_to_response(self.get_template(), params)
        win = BaseExtWindow()
        win.height = 500
        win.width = 400
        return OperationResult(code=win.get_script()).get_http_response()
