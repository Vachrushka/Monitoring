# from background_task import background
# from logging import getLogger
#
# logger = getLogger(__name__)
# #  python manage.py process_tasks --sleep 20
# @background(schedule=60)
# def demo_task(message):
#     logger.debug('demo_task. message={0}'.format(message))
#
#
# @background(schedule=3600)
# def update_leadtable_task():
#     logger.debug('update_leadtable_task started')
#
#     # получить все данные из всех таблиц
#     # сформировать новую таблицу
#
#     # получить старую таблицу, получить прирост для всех полей
#     # сохрантиь
#
#     logger.debug('update_leadtable_task end')
#
