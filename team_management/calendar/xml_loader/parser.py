import xml.etree.ElementTree as ET
from datetime import date


class XMLCalendarParser:
    def __init__(self, xml_path):
        self.xml_path = xml_path

    def get_calendar(self):
        if not self.xml_path:
            raise FileNotFoundError('Не найден файл!')

        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        days = root.find('days')
        result = {}
        if days:
            for day in days.findall("day"):
                _year = int(root.attrib.get('year'))
                _month = int(day.attrib.get('d').split('.')[0])
                _day = int(day.attrib.get('d').split('.')[1])
                # если 1 - нерабочий, если 2 - сокращенный
                _sokr = int(day.attrib.get('t')) > 1
                result.update(
                    {date(year=_year, month=_month, day=_day): _sokr}
                )
        return result

