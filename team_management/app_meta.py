from django.conf.urls import url
from team_management.actions import MainTMDesktopPack
from team_management.urls import tm_controller, team_manager_view


def register_actions():
    tm_controller.packs.extend([
        MainTMDesktopPack(),
    ])


def register_urlpatterns():
    return (url(r'^team_management/', team_manager_view),)
