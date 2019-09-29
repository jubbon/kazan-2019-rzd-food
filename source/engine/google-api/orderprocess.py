import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import uuid
import random
import requests
import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(sys.path[0], '../'))

from hereapi import run as hereapi

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
                'Phone':'89063660240',
                'Photo': 'https://rzd-food.s3.amazonaws.com/kulikov.jpg',
                'Status': 'В ожидании',
                'Percent': 0
                },
             {'Role': 'Курьер',
                'FirstName': 'Айдар',
                'LastName':'Сайфуллин',
                'FIO':'Айдар Сайфуллин',
                'Phone':'89053757057',
                'Photo': 'https://rzd-food.s3.amazonaws.com/aidar.jpg',
                'Status': 'В ожидании',
                'Percent': 0
                }]

while True:
    # Чтение данных для формирования заказа
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Корзина!A2:G',
        majorDimension='ROWS'
    ).execute()

    # генерация уникального идентификатора заказа
    orderCount = 0
    uuids = list()
    total = list()
    basket = dict()

    if 'values' in values:
        orderCount = len(values['values'])
        
        for elem in values['values']:
            if elem:
                if len(elem[0]) == 0:
                    elem[0] = str(uuid.uuid4().hex)[:8]

        # подсчет стоимости
        for elem in values['values']:
            if elem:
                if len(elem) < 6:
                    elem.append('')
                if len(elem) < 7:
                    elem.append('')
                try:
                    elem[5] = str(int(elem[3]) * int(elem[4]))
                except:
                    print ('type error')

        # обновление данных в корзине
        uuids = [[values['values'][number][0]] for number in range(len(values['values']))]
        total = [[values['values'][number][5]] for number in range(len(values['values']))]
        #print (uuids)
        #print (total)
        basket = values

    values = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Корзина!A2:A" + str(2+len(uuids)),
                "majorDimension": "ROWS",
                "values": uuids },
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
        range='Меню!A2:H',
        majorDimension='ROWS'
    ).execute()

    # Чтение таблицы остановок по городам, где стоянка более 10 минут
    stopStations = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Города!A2:E',
        majorDimension='ROWS'
    ).execute()

    orderCount = 0
    if 'values' in values:
        orderCount = len(values['values'])

    # индекс для вставки
    orderCount = orderCount + 2

    uuids = list()
    tickets = list()
    cities = list ()
    comments = list()
    totals = list()
    status=list()
    desks = list()
    picture = list()
    bonus = list()
    deliveryTime = list()
    reldeltime = list ()
    cafes = list()
    cafes_coord = list()
    station_cood = list()

    if 'values' in basket:
        uuids = [[basket['values'][number][0]] for number in range(len(basket['values']))]
        tickets = [['76741487825338'] for number in range(len(basket['values']))]
        cities = [[basket['values'][number][1]] for number in range(len(basket['values']))]
        comments = [[basket['values'][number][6]] for number in range(len(basket['values']))]
        totals = [[basket['values'][number][5]] for number in range(len(basket['values']))]
        status = [['Не отправлен'] for number in range(len(basket['values']))]

        for number in range(len(basket['values'])):
            index = basket['values'][number][2]
            for elem in menus['values']:
                if elem:
                    if elem[0] == index:
                        desks.append ([elem[2]])
                        picture.append ([elem[6]])
                        bonus.append ([elem[5]])
                        cafes.append ([elem[3]])
                        cafes_coord.append ([elem[7]])

        for number in range(len(cities)):            
            name = cities[number][0]
            tickNum = tickets[number][0]
            for stat in range(len(stopStations)):
                if stopStations['values'][stat][0] == tickNum:
                    if stopStations['values'][stat][1] == name:
                        deliveryTime.append ([stopStations['values'][stat][2]])
                        station_cood.append ([stopStations['values'][stat][4]])
                        break

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
                {"range": "Заказы!O" + str(orderCount) + ":O" + str(orderCount+len(cafes)),
                "majorDimension": "ROWS",
                "values": cafes },
                {"range": "Заказы!P" + str(orderCount) + ":P" + str(orderCount+len(cafes_coord)),
                "majorDimension": "ROWS",
                "values": cafes_coord },
                {"range": "Заказы!Q" + str(orderCount) + ":Q" + str(orderCount+len(station_cood)),
                "majorDimension": "ROWS",
                "values": station_cood },
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

    # Перрон
    if len (uuids) > 0:
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Перрон!A2:D',
            majorDimension='ROWS'
        ).execute()
        
        orderonWayCount = 0
        if 'values' in values:
            orderonWayCount = len(values['values'])
        orderonWayCount = orderonWayCount+2

        location = [['Платформа ' + str(random.randint(1, 5))  +', путь ' + str(random.randint(1, 10)) + ', вагон ' + str(random.randint(1, 20))] for number in range(len (uuids))]
        firstColor = [['https://rzd-food.s3.amazonaws.com/color-' + str(random.randint(1, 8))  +'.jpg'] for number in range(len (uuids))]
        secondColor = [['https://rzd-food.s3.amazonaws.com/color-' + str(random.randint(1, 8))  +'.jpg'] for number in range(len (uuids))]
        
        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "Перрон!A" + str(orderonWayCount) + ":A" + str(orderonWayCount+len(uuids)),
                    "majorDimension": "ROWS",
                    "values": uuids },
                    {"range": "Перрон!B" + str(orderonWayCount) + ":B" + str(orderonWayCount+len(location)),
                    "majorDimension": "ROWS",
                    "values": location },
                    {"range": "Перрон!C" + str(orderonWayCount) + ":C" + str(orderonWayCount+len(firstColor)),
                    "majorDimension": "ROWS",
                    "values": firstColor },
                    {"range": "Перрон!D" + str(orderonWayCount) + ":D" + str(orderonWayCount+len(secondColor)),
                    "majorDimension": "ROWS",
                    "values": secondColor }
            ]
            }
        ).execute()
    
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Доставка!A2:A',
        majorDimension='ROWS'
    ).execute()
    deliveryHistoryCount = len(values['values'])

    url = f"https://k7qml3o0db.execute-api.us-east-1.amazonaws.com/dev/send_sms"
    delivToHist = list()
    for orderuuid in uuids:
        count = len ( couriers)
        coutierIndex = random.randint(0, count-1) 

        now = datetime.now()
        delstr = deliveryTime[uuids.index(orderuuid)][0]
        deltime= datetime.strptime(delstr, '%d.%m.%Y %H:%M')
        if deltime > now:
            delta = deltime - now
            if delta.seconds < 10800:
                response = requests.post(url, json={
                    'phone': couriers[coutierIndex]['Phone'],
                    'message': 'Сформирован заказ ' + orderuuid[0] + ' Доставка ' + str(deliveryTime[uuids.index(orderuuid)][0]) + 
                    ' на станцию' 
                    + cities[uuids.index(orderuuid)]
                })
                time.sleep(5)
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
        cour.append( deliveryTime[uuids.index(orderuuid)][0] )
        A = cafes_coord[uuids.index(orderuuid)][0]
        B = station_cood [uuids.index(orderuuid)][0]
        A = A.replace(" ", "")
        B = B.replace(" ", "")
        cour.append( hereapi.getMinimumTime(A, B ))
        delivToHist.append(cour)

    values = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Доставка!A" + str(deliveryHistoryCount+2) + ":K" + str(deliveryHistoryCount +2 +len(delivToHist)),
                "majorDimension": "ROWS",
                "values": delivToHist }    ]
            }
    ).execute()

    # Чистка от старого заказа
    val = [['','','','','','',''] for number in range(7)]
    values = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Корзина!A2:G" + str(orderCount+len(val)),
                "majorDimension": "COLUMNS",
                "values": val }
        ]
        }
    ).execute()
    time.sleep(6)
