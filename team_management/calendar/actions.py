import datetime

from m3 import OperationResult
from m3.actions import ActionPack, Action, logger

from team_management.calendar.models import Holidays
from team_management.calendar.xml_loader.main import get_calendar


class HolidaysPack(ActionPack):
    url = '/holidays'
    shortname = url[1:]

    def __init__(self):
        super().__init__()
        self.some_ajax = FillCalendar()
        self.actions.append(self.some_ajax)


class FillCalendar(Action):
    url = '/fill_calendar'
    shortname = url[1:]

    def run(self, request, context):
        _calendar = get_calendar()
        _bulk_create_list = []
        if _calendar:
            Holidays.objects.filter(
                holiday_date__year=datetime.datetime.now().year
            ).delete()
        for _holiday_date, _sokr in _calendar.items():
            _bulk_create_list.append(Holidays(
                holiday_date=_holiday_date,
                sokr=_sokr
            ))
        Holidays.objects.bulk_create(_bulk_create_list)
        logger.log(msg='Заполнена таблица праздников и выходных', level=1)

        return OperationResult.by_message(
            'Обновлена таблица праздников')
