import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_spreadsheet(title, key, scope):
    creds = ServiceAccountCredentials.from_json_keyfile_name(key, scope)
    client = gspread.authorize(creds)

    sheet = client.open(title).sheet1

    return sheet
