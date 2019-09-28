import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

# Файл, полученный в Google Developer Console
CREDENTIALS_FILE = 'creds.json'
# ID Google Sheets документа
spreadsheet_id = '1CwavDhdobVa6PY82XPRONOMZjvtKld8JiYWHu4I7OQQ'

# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

# Чтение данных для формирования заказа
values = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Лист2!B2:C',
    majorDimension='ROWS'
).execute()

menuCount = len(values['values'])
ordermenu = dict()
for elem in values['values']:
    if elem:
        if elem[1] == '1':
            ordermenu[elem[0]]=elem[1]

# Чистка от старого заказа
val = [("","") for number in range(menuCount)]
values = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Лист1!B2:C" + str(2+menuCount),
            "majorDimension": "ROWS",
            "values": val }
    ]
    }
).execute()

# Запись данных для оформления заказа
if len(ordermenu) != 0:
    values = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Лист1!B2:C" + str(2+len(ordermenu)),
                "majorDimension": "ROWS",
                "values": list(ordermenu.items()) }
        ]
        }
    ).execute()
