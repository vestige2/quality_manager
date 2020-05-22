import requests
import os
import datetime


class XMLLoader:
    """
    Делает запрос по load() на сайт с xml путем производственного календаря
    параметризуется адресом сайта и файлом, в который записывается календарь
    """
    def __init__(self, url='', xml_file_path=''):
        current_year = datetime.datetime.now().year
        # откуда забираем данные
        self.url = (
                url or
                f'http://xmlcalendar.ru/data/ru/{current_year}/calendar.xml'
        )

        # в какой файл записываем
        self.xml_file_path = (
                xml_file_path or
                os.path.join(
                    os.path.abspath(os.curdir),
                    f'team_management/calendar/xml_loader/loaded_xml/{datetime.datetime.now().year}.xml')
        )

    def load(self):
        # to_broad :(
        try:
            r = requests.get(self.url)  # делаем запрос
            f = open(self.xml_file_path, "wb")
            f.write(r.content)  # записываем содержимое в файл; как видите - content запроса
            f.close()
            result = self.xml_file_path
        except:
            result = None

        return result
