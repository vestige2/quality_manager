import os
from collections import defaultdict
from decimal import Decimal

import xlrd

from quality_manager.settings import BASE_DIR

wl_data = []
team = (
    'a.morozov',
    'm.repin',
    'kirov',
    'sergey.korolev',
    't.morozova',
    'efimov',
    'a.yuzhakov',
    'n.kapralova',
    'n.ryzhenkov',
    's.khaliullin',
    's.novozhilov',
    's.voronov',
    'e.eremin'
)

types_of_w = (
    'Разработка',
    'Доработка',
    'Исправление'
)

for i in (1, 2):
    print(f'Файл {i}')

    rb = xlrd.open_workbook(
        os.path.join(BASE_DIR,
                     f'quality_manager/../quality_manager/../'
                     f'team_management/jira_integration/{i}.xls'
                     ), formatting_info=True)
    sheet = rb.sheet_by_index(0)

    for rownum in range(sheet.nrows):
        row = sheet.row_values(rownum)
        if row[25] in types_of_w:
            # задача, юзернейм, часов списано, компоненты, перв.оценка
            wl_data.append((row[0], row[5], row[21], row[11], row[22]))
print(wl_data)

tasks_set = set()

rb = xlrd.open_workbook(
    os.path.join(BASE_DIR,
                 f'quality_manager/../quality_manager/../'
                 f'team_management/jira_integration/3.xls'
                 ),
    formatting_info=True)
sheet = rb.sheet_by_index(0)

for rownum in range(sheet.nrows):
    row = sheet.row_values(rownum)
    if 'BOZIK' in row[4] and row[6]:
        tasks_set.add((row[4].strip(), int(row[6])/3600))

print(tasks_set)


def get_info_by_tasks_set(tasks_set):
    result_tasks = defaultdict(tuple)
    # в разрезе тасков
    for t in tasks_set:
        orig = t[1]
        task_key = t[0]
        total_time = sum([Decimal(x[2]) for x in wl_data if x[0] == task_key])
        user_names = ', '.join(
            set([x[1] for x in wl_data if x[0] == task_key]))
        if user_names:
            result_tasks[task_key] = (user_names, orig, total_time)
    return result_tasks


result_tasks = get_info_by_tasks_set(tasks_set)
for k, v in result_tasks.items():
    print(f'{k} | {v[0]} | {v[1]} | {int(v[2])}')

# в разрезе компонентов
components_set = set()
for row in wl_data:
    if row[3]:
        if ';' in row[3]:
            for _str in row[3].split(';'):
                components_set.add(_str)
        else:
            components_set.add(row[3])

tasks_set = {(x[0], x[4],  x[3]) for x in wl_data if 'BOZIK' in x[0]}
result_tasks = get_info_by_tasks_set(tasks_set)
result = defaultdict(list)
for component in components_set:
    tasks_for_comp = [x for x in tasks_set if component in x[2]]
    orig = int(sum(Decimal(result_tasks[x[0]][1]) if result_tasks[x[0]] else 0 for x in tasks_for_comp))
    total = int(sum(Decimal(result_tasks[x[0]][2]) if result_tasks[x[0]] else 0 for x in tasks_for_comp))
    print(f'{component} | {total/orig}')


