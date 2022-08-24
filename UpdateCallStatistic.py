from authentication import authentication
from fast_bitrix24 import Bitrix
from time import strftime
from time import time
from time import gmtime
from time import strptime
from datetime import timedelta

# Считывание файла authentication.txt

webhook = authentication('Bitrix')
b = Bitrix(webhook)

employee_numbers = [
    '+79991174816',     # Жанна Умалатова
    '+79991174814',     # Елена Коршакова
    '+79991174815',     # Екатерина Плотникова
    '+79991174818',     # Ольга Цветкова
    '+79991174812',     # Мария Боцула
    '+79522806626',     # МОЙ
    '+79991174813',     # Любовь Корсунова
    '+79991174826',     # Борис
]

allowed_departments = b.get_all('user.get', {'filter': {'UF_DEPARTMENT': ['231', ]}})
allowed_numbers = []
for employee in allowed_departments:
    allowed_numbers.append(employee['WORK_PHONE'])

def update_call_statistic(req):
    """
    :param req: request.form
    :return: Обновление или создание элемента в УС "Статистика звонков"
    """

    if req['data[CALL_TYPE]'] not in ['1', ] or\
            req['data[PORTAL_NUMBER]'] not in employee_numbers or\
            req['data[CALL_FAILED_CODE]'] != '200':
        return

    client_number = req['data[PHONE_NUMBER]']
    employee_number = req['data[PORTAL_NUMBER]']
    call_duration_seconds = req['data[CALL_DURATION]']
    call_duration = gmtime(int(req['data[CALL_DURATION]']))
    month_string = {
        '01': 'Январь',
        '02': 'Февраль',
        '03': 'Март',
        '04': 'Апрель',
        '05': 'Май',
        '06': 'Июнь',
        '07': 'Июль',
        '08': 'Август',
        '09': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
    }
    current_date = f'{month_string[strftime("%m")]} {strftime("%Y")}'

    # ID контакта через номер телефона

    contact = b.get_all('telephony.externalCall.searchCrmEntities', {'PHONE_NUMBER': client_number})
    contact_id = contact[0]['CRM_ENTITY_ID']

    # Компании, связанные с контактом | заполнение УС "Статистика звонков"

    companies = b.get_all('crm.contact.company.items.get', {'id': contact_id})
    for company in companies:
        list_elements = b.get_all('lists.element.get', {
            'IBLOCK_TYPE_ID': 'lists',
            'IBLOCK_ID': '175',
            'filter': {
                'PROPERTY_1299': company['COMPANY_ID'],
                'NAME': current_date,
            }
        }
                                  )

        # Если нет элемента списка для компании на текущую дату - создается новый элемент

        if len(list_elements) == 0:
            b.call('lists.element.add', {
                'IBLOCK_TYPE_ID': 'lists',
                'IBLOCK_ID': '175',
                'ELEMENT_CODE': time(),
                'fields': {
                    'NAME': current_date,   # Название == месяц и год
                    'PROPERTY_1303': strftime("%H:%M:%S", call_duration),   # Продолжительность звонка
                    'PROPERTY_1299': company['COMPANY_ID'],     # Привязка к компании
                    'PROPERTY_1305': '1',    # Количество звонков
                }
            }
                   )

        # Если найден элемент - он обновляется

        else:
            for element in list_elements:
                for field_value in element['PROPERTY_1303']:
                    element_duration = element['PROPERTY_1303'][field_value]
                for field_value in element['PROPERTY_1305']:
                    element_call_count = element['PROPERTY_1305'][field_value]

            # Форматирование времени в секунды и суммирование с длительностью звонка

            element_time = strptime(element_duration, "%H:%M:%S")
            element_seconds = timedelta(
                hours=element_time.tm_hour,
                minutes=element_time.tm_min,
                seconds=element_time.tm_sec
            ).seconds
            new_seconds = int(element_seconds) + int(call_duration_seconds)
            new_time = gmtime(new_seconds)

            b.call('lists.element.update', {
                'IBLOCK_TYPE_ID': 'lists',
                'IBLOCK_ID': '175',
                'ELEMENT_ID': element['ID'],
                'fields': {
                    'NAME': element['NAME'],
                    'PROPERTY_1303': strftime("%H:%M:%S", new_time),    # Продолжительность звонков
                    'PROPERTY_1299': company['COMPANY_ID'],     # Привязка к компании
                    'PROPERTY_1305': str(int(element_call_count) + 1)   # Количество звонков
                }
            }
                   )

            # Если лимит продолжительности звонков превышен - ставится задача

            for field_value in element['PROPERTY_1307']:
                element_max_duration = element['PROPERTY_1307'][field_value]
            element_max_duration = strptime(element_max_duration, "%H:%M:%S")
            element_max_duration = timedelta(
                hours=element_max_duration.tm_hour,
                minutes=element_max_duration.tm_min,
                seconds=element_max_duration.tm_sec
            ).seconds
            if new_seconds > element_max_duration:
                b.call('tasks.task.add', {
                    'fields': {
                        'TITLE': f"Для компании {company['TITLE']} превышен лимит звонков",
                        'GROUP_ID': '13',
                        'RESPONSIBLE_ID': '311',
                        'UF_CRM_TASK': "CO_" + company['COMPANY_ID']
                    }
                }
                       )