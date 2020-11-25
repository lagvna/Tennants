import gspread
from oauth2client.service_account import ServiceAccountCredentials
import confighandler

def get_spreadsheet(subsheet):
    creds = ServiceAccountCredentials.from_json_keyfile_name(confighandler.get_google_key(),
    														 confighandler.get_google_scope())
    client = gspread.authorize(creds)

    sheet = client.open(
        confighandler.get_google_sheet()).worksheet(confighandler.get_google_subsheet(subsheet))

    return sheet