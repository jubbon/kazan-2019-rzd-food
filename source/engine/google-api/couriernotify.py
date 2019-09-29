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

while True:
    # Чтение таблицы доставки
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Доставка!A2:Q',
        majorDimension='ROWS'
    ).execute()

    if 'values' not in values:
        continue

    for elem in values['values']:
        if elem:
            if len(elem) < 10:
                elem.append('')
            if len(elem) < 11:
                elem.append('')
            if len(elem) < 12:
                elem.append('')

    status = [[values['values'][number][11]] for number in range(len(values['values']))]
    delAtTime = [[values['values'][number][9]] for number in range(len(values['values']))]
    phones = [[values['values'][number][5]] for number in range(len(values['values']))]
    uuid = [[values['values'][number][0]] for number in range(len(values['values']))]

    # Чтение таблицы заказов
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Заказы!A2:C',
        majorDimension='ROWS'
    ).execute()

    if 'values' in values:
        orderuuid = [[values['values'][number][0]] for number in range(len(values['values']))]
        stationname = [[values['values'][number][2]] for number in range(len(values['values']))]

        url = f"https://k7qml3o0db.execute-api.us-east-1.amazonaws.com/dev/send_sms"
        for number in range(len(status)):
            if len(status[number][0]) == 0:
                now = datetime.now()
                delstr = delAtTime[number][0]
                deltime= datetime.strptime(delstr, '%d.%m.%Y %H:%M')
                if deltime > now:
                    delta = deltime - now
                    if delta.seconds < 10800:
                        try:
                            response = requests.post(url, json={
                                'phone': phones[number][0],
                                'message': 'Сформирован заказ ' + uuid[number][0] + ' Доставка '
                                + delstr + ' на станцию' 
                                + stationname[orderuuid.index(uuid[number])][0]
                            })
                            print ('Send SMS: ' + phones[number][0])
                        except:
                            print ('Error sms sending or find order uuid')

                        values = service.spreadsheets().values().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body={
                            "valueInputOption": "USER_ENTERED",
                            "data": [
                                {"range": "Доставка!L" + str(number+2) + ":L" + str(number+2),
                                "majorDimension": "ROWS",
                                "values": [[str(now)]] }    ]
                            }
                            ).execute()
    time.sleep(15)
