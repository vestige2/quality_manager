from django.conf import settings
from m3.actions import urls, ActionController

TM_DEF_ROOT = settings.ROOT_URL + '/team_management'
tm_controller = ActionController(
    name='Главный контроллер ТМ'
)
tm_controller.url = TM_DEF_ROOT


def team_manager_view(request):
    """
    Основная view менеджера команд.
    """
    # Если запрос пришел на урл /team_management то адресуем пользователя
    if request.path in (TM_DEF_ROOT, TM_DEF_ROOT+'/'):
        request.path = urls.get_url(TM_DEF_ROOT + '/desktop/show')
        return tm_controller.process_request(request)
    else:
        return tm_controller.process_request(request)
        # authenticated = request.user.is_authenticated
        # if authenticated or request.path == urls.get_url('login'):
        #     result = tm_controller.process_request(request)
        #     return result
        # elif request.path == '/team_management':
        #     # а не авторизованных авторизуем:
        #     request.path = urls.get_url(TM_DEF_ROOT + '/desktop/show')
        #     return tm_controller.process_request(request)
        # else:
        #     result = tm_controller.process_request(request)
        #     return result