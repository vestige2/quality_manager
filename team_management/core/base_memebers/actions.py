from m3.actions import ActionPack


class MemberPack(ActionPack):
    """
    Управление членами команды
    """
    url = '/members'
    shortname = url[1:]