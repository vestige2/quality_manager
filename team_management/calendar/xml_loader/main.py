from team_management.calendar.xml_loader.loader import XMLLoader
from team_management.calendar.xml_loader.parser import XMLCalendarParser


class Calendar:
    def __init__(self):
        self.loader = XMLLoader()
        xml_path = self.loader.load()
        self.parser = XMLCalendarParser(xml_path)

    @property
    def calendar(self):
        calendar = self.parser.get_calendar()

        return calendar


def get_calendar():
    """
    :return: словарь праздников, выходных
     и сокращенных дней вида
    {дата: сокращенный ли день}
         True - сокращенный
         False - нерабочий полностью
    """
    x = Calendar().calendar

    return x


if __name__ == "__main__":
    get_calendar()



