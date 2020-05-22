from team_management.urls import tm_controller
from team_management.core.teams.actions import TeamPack


def register_actions():
    tm_controller.packs.extend([
        TeamPack(),
    ])
