def _get_all_grids(item, lst=None):
    u""" Список всех гридов формы включая вложенные в контейнеры.

    :rtype: list

    """
    _lst = lst or []
    if isinstance(item, int):
        lst.append(item)
    elif isinstance(item, list):
        for it in item:
            _get_all_grids(it, _lst)
    return _lst


def _get_all_grids2(item, lst=None):
    u""" Список всех гридов формы включая вложенные в контейнеры.

    :rtype: list

    """
    # lst = lst or []
    if isinstance(item, int):
        lst.append(item)
    elif isinstance(item, list):
        for it in item:
            _get_all_grids2(it, lst)
    return lst


t = []
print(_get_all_grids([1, 2, [3, 4, 5, [6, 7, 8, [9, 10]]]], t))
print(t)


x = []
print(_get_all_grids2([1, 2, [3, 4, 5, [6, 7, 8, [9, 10]]]], x))
print(x)



