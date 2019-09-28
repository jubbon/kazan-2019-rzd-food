import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import time

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
    time.sleep(20)
    # Чтение таблицы заказов
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Заказы!F2:F',
        majorDimension='ROWS'
    ).execute()

    if 'values' in values:
        status = [[values['values'][number][0]] for number in range(len(values['values']))]

        for elem in status:
            if elem[0] == 'Не отправлен':
                elem[0] = 'Заказ формируется'

        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Заказы!F2:F" + str(2+len(status)),
                "majorDimension": "ROWS",
                "values": status }]
            }
            ).execute()
            
    

