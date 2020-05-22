from team_management.urls import tm_controller
from team_management.calendar.actions import HolidaysPack


def register_actions():
    tm_controller.packs.extend([
        HolidaysPack(),
    ])
