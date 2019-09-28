import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import uuid
import random
import requests

# Файл, полученный в Google Developer Console
CREDENTIALS_FILE = 'creds.json'
# ID Google Sheets документа
spreadsheet_id = '1ilnE1sihoVoFDY_ako53FmlTjk9VM0wt31Vuj6dN1oc'

# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

# Курьеры
couriers = [{'Role': 'Курьер',
                'FirstName': 'Дмитрий',
                'LastName':'Куликов',
                'FIO':'Дмитрий Куликов',
                'Phone':'+79063660240',
                'Photo': 'https://rzd-food.s3.amazonaws.com/kulikov.jpg',
                'Status': 'В ожидании',
                'Percent': 0
                },
             {'Role': 'Курьер',
                'FirstName': 'Айдар',
                'LastName':'Сайфуллин',
                'FIO':'Айдар Сайфуллин',
                'Phone':'+79053757057',
                'Photo': 'https://rzd-food.s3.amazonaws.com/aidar.jpg',
                'Status': 'В ожидании',
                'Percent': 0
                }]

# Чтение данных для формирования заказа
values = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Корзина!A2:G',
    majorDimension='ROWS'
).execute()

# генерация уникального идентификатора заказа
orderCount = len(values['values'])
for elem in values['values']:
    if elem:
        if len(elem[0]) == 0:
            elem[0] = uuid.uuid4().hex

# подсчет стоимости
for elem in values['values']:
    if elem:
        if len(elem) < 6:
            elem.append('')
        if len(elem) < 7:
            elem.append('')
        elem[5] = str(int(elem[3]) * int(elem[4]))

# обновление данных в корзине
uuid = [[values['values'][number][0]] for number in range(len(values['values']))]
total = [[values['values'][number][5]] for number in range(len(values['values']))]
#print (uuid)
#print (total)
basket = values

values = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Корзина!A2:A" + str(2+len(uuid)),
            "majorDimension": "ROWS",
            "values": uuid },
            {"range": "Корзина!F2:F" + str(1+len(total)),
            "majorDimension": "ROWS",
            "values": total }
    ]
    }
).execute()

# Чтение таблицы заказов
values = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Заказы!A2:A',
    majorDimension='ROWS'
).execute()

# Чтение таблицы меню
menus = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Меню!A2:G',
    majorDimension='ROWS'
).execute()

# Чтение таблицы остановок по городам, где стоянка более 10 минут
stopStations = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Города!A2:D',
    majorDimension='ROWS'
).execute()

orderCount = len(values['values'])

# индекс для вставки
orderCount = orderCount + 2

uuids = [[basket['values'][number][0]] for number in range(len(basket['values']))]
tickets = [['76741487825338'] for number in range(len(basket['values']))]
cities = [[basket['values'][number][1]] for number in range(len(basket['values']))]
comments = [[basket['values'][number][6]] for number in range(len(basket['values']))]
totals = [[basket['values'][number][5]] for number in range(len(basket['values']))]
status = [['Не отправлен'] for number in range(len(basket['values']))]

desks = list()
picture = list()
bonus = list()
for number in range(len(basket['values'])):
    index = basket['values'][number][2]
    for elem in menus['values']:
        if elem:
            if elem[0] == index:
               desks.append ([elem[2]])
               picture.append ([elem[6]])
               bonus.append ([elem[5]])

deliveryTime = list()
for number in range(len(cities)):            
    name = cities[number][0]
    tickNum = tickets[number][0]
    for stat in range(len(stopStations)):
        if stopStations['values'][stat][0] == tickNum:
            if stopStations['values'][stat][1] == name:
                deliveryTime.append ([stopStations['values'][stat][2]])
                break

reldeltime = list ()
useIndex = orderCount 
for number in range(len(basket['values'])):
    reldeltime.append(['=G' + str(useIndex) + '-ТДАТА()'])
    useIndex = useIndex + 1

# Запись данных для оформления заказа
values = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Заказы!A" + str(orderCount) + ":A" + str(orderCount+len(uuids)),
            "majorDimension": "ROWS",
            "values": uuids },
            {"range": "Заказы!B" + str(orderCount) + ":B" + str(orderCount+len(tickets)),
            "majorDimension": "ROWS",
            "values": tickets },
            {"range": "Заказы!C" + str(orderCount) + ":C" + str(orderCount+len(cities)),
            "majorDimension": "ROWS",
            "values": cities },
            {"range": "Заказы!N" + str(orderCount) + ":N" + str(orderCount+len(comments)),
            "majorDimension": "ROWS",
            "values": comments },
            {"range": "Заказы!E" + str(orderCount) + ":E" + str(orderCount+len(totals)),
            "majorDimension": "ROWS",
            "values": totals },
            {"range": "Заказы!F" + str(orderCount) + ":F" + str(orderCount+len(status)),
            "majorDimension": "ROWS",
            "values": status },
            {"range": "Заказы!G" + str(orderCount) + ":G" + str(orderCount+len(deliveryTime)),
            "majorDimension": "ROWS",
            "values": deliveryTime },
            {"range": "Заказы!H" + str(orderCount) + ":H" + str(orderCount+len(reldeltime)),
            "majorDimension": "ROWS",
            "values": reldeltime },
            {"range": "Заказы!D" + str(orderCount) + ":D" + str(orderCount+len(desks)),
            "majorDimension": "ROWS",
            "values": desks },
            {"range": "Заказы!M" + str(orderCount) + ":M" + str(orderCount+len(picture)),
            "majorDimension": "ROWS",
            "values": picture },
            {"range": "Заказы!L" + str(orderCount) + ":L" + str(orderCount+len(bonus)),
            "majorDimension": "ROWS",
            "values": bonus }
    ]
    }
).execute()

values = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Доставка!A2:A',
    majorDimension='ROWS'
).execute()
deliveryHistoryCount = len(values['values'])


delivToHist = list()
for orderuuid in uuids:
    count = len ( couriers)
    coutierIndex = random.randint(0, count-1) 
    url = f"https://k7qml3o0db.execute-api.us-east-1.amazonaws.com/dev/send_sms"
    response = requests.post(url, json={
            'phone': couriers[coutierIndex]['Phone'],
            'message': 'Сформирован заказ: ' +  orderuuid[0] 
        })
    cour = list()
    cour.append( orderuuid[0] )    
    cour.append( couriers[coutierIndex]['Role'] )
    cour.append( couriers[coutierIndex]['FirstName'] )
    cour.append( couriers[coutierIndex]['LastName'] )
    cour.append( couriers[coutierIndex]['FIO'] )
    cour.append( couriers[coutierIndex]['Phone'] )
    cour.append( couriers[coutierIndex]['Photo'] )
    cour.append( couriers[coutierIndex]['Status'] )
    cour.append( couriers[coutierIndex]['Percent'] )
    delivToHist.append(cour)

values = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Доставка!A" + str(deliveryHistoryCount+2) + ":I" + str(deliveryHistoryCount +2 +len(delivToHist)),
            "majorDimension": "ROWS",
            "values": delivToHist }    ]
        }
).execute()
'''
# Чистка от старого заказа
val = [[''] for number in range(7)]
values = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Корзина!A4:G" + str(orderCount+len(val)),
            "majorDimension": "ROWS",
            "values": val }
    ]
    }
).execute()
'''