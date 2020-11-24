from configparser import SafeConfigParser
import gspread
from oauth2client.service_account import ServiceAccountCredentials

CONFIG_FILE = '/home/lagvna/config.ini'
config_parser = SafeConfigParser()
config_parser.read(CONFIG_FILE)
key = config_parser.get('googledrive', 'key')
scope = config_parser.get('googledrive', 'scope')

def get_spreadsheet(subsheet):
    creds = ServiceAccountCredentials.from_json_keyfile_name(key, scope)
    client = gspread.authorize(creds)

    sheet = client.open(
        config_parser.get(
            'googledrive', 'sheet')).worksheet(config_parser.get('googledrive', subsheet))

    return sheet

def get_folder(name):
    return config_parser.get('folders', name)

def get_smpiast_url(aid):
    return config_parser.get('smpiast'+aid, 'url')

def get_smpiast_login(aid):
    return config_parser.get('smpiast'+aid, 'login')

def get_smpiast_password(aid):
    return config_parser.get('smpiast'+aid, 'password')

def get_tauron_url(aid):
    return config_parser.get('tauron'+aid, 'url')

def get_tauron_login(aid):
    return config_parser.get('tauron'+aid, 'login')

def get_tauron_password(aid):
    return config_parser.get('tauron'+aid, 'password')

def get_pgnig_url():
    return config_parser.get('pgnig', 'url')

def get_pgnig_login():
    return config_parser.get('pgnig', 'login')

def get_pgnig_password():
    return config_parser.get('pgnig', 'password')
