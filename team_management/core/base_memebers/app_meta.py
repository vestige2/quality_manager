from team_management.urls import tm_controller
from team_management.core.base_memebers.actions import MemberPack


def register_actions():
    tm_controller.packs.extend([
        MemberPack(),
    ])
