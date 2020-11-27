import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .confighandler import get_google_key, get_google_scope, get_google_sheet, get_google_subsheet

def get_spreadsheet(subsheet):
    creds = ServiceAccountCredentials.from_json_keyfile_name(get_google_key(),
    							 							 get_google_scope())
    client = gspread.authorize(creds)

    sheet = client.open(get_google_sheet()).worksheet(get_google_subsheet(subsheet))

    return sheet
