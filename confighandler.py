from configparser import SafeConfigParser

CONFIG_FILE = '/home/lagvna/config.ini'
config_parser = SafeConfigParser()
config_parser.read(CONFIG_FILE)


def get_google_key():
    return config_parser.get('googledrive', 'key')

def get_google_scope():
    return config_parser.get('googledrive', 'scope')

def get_google_sheet():
    return config_parser.get('googledrive', 'sheet')

def get_google_subsheet(subsheet):
    return config_parser.get('googledrive', subsheet)

def get_folder(name):
    return config_parser.get('folders', name)

def get_file(name):
    return config_parser.get('files', name)

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

def get_pushes(aid):
    return config_parser.get('pushes', 'apartment'+aid)

def get_internet_cost(aid):
    return config_parser.get('internet', 'apartment'+aid)
    