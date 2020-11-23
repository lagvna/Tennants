#   Copyright (c) Jarosław Mirek
import os
import sys
import logging
import click
import pandas as pd
from shutil import copyfile
from pathlib import Path
import fileinput
from gsshandler import get_spreadsheet
from configparser import SafeConfigParser
from scrape import *
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


config_file = '/home/lagvna/config.ini'
config_parser = SafeConfigParser()
config_parser.read(config_file)
key = config_parser.get('googledrive', 'key')
scope = config_parser.get('googledrive', 'scope')

@click.group()
@click.option('--quiet', default=False, is_flag=True, help='Run in silent mode')
def cli(quiet):
    """
    tennaants is a command line program which facilitates the management of renting apartments.
    It allows to manage tennants, apartments, generate lease agreements and calculate bills
    from SM Piast Wroclaw, Tauron and PGNiG. It operates on documents held on Google Drive.
    """
    if quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@cli.command('lsl', help='List all landlords')
def list_all_landlords():
    data = pd.DataFrame(get_spreadsheet(config_parser.get('googledrive', 'landlords'), key, scope).get_all_records())
    print(data)

@cli.command('lst', help='List all tennants')
def list_all_tennants():
    data = pd.DataFrame(get_spreadsheet(config_parser.get('googledrive', 'tennants'), key, scope).get_all_records())
    print(data)

@cli.command('lsa', help='List all apartments')
def list_all_apartments():
    data = pd.DataFrame(config_parser.get('googledrive', 'apartments').get_all_records())
    print(data)

@cli.command('genbil', help='Generate bills for the current period for a particular tennant')
# @click.option('--aid', required=True, help='Apartment ID')
@click.option('--month', multiple=True, required=True, help='For which months bills should be generated')
@click.option('--year', required=True, help='For which year bills should be generated')
def generate_bills(month, year):
    months = list(month)
    water = get_smpiast_costs(months, year)
    electricity = get_tauron_costs(months, year)
    gas = get_pgnig_costs(months, year)

    df = pd.DataFrame(columns=['Miesiąc', 'Energia elektryczna', 'Gaz', 'Woda ciepła', 
        'Woda zimna', 'Razem wszystkie opłaty', 'Razem na jedną osobę'])

    print(df)
    df.to_csv(r'oplaty.csv')

    # print(water)
    # print(electricity)
    # print(gas)


def send_bills():
    pass

def send_agreement():
    pass

@cli.command('genagr', help='Generate lease agreement for a particular tennant')
@click.option('--tid', required=True, help='Tennant ID')
@click.option('--lid', required=True, help='Landlord ID')
@click.option('--aid', required=True, help='Apartment ID')
@click.option('--fr', required=True, help='From date')
@click.option('--to', required=True, help="To date")
@click.option('--rent', required=True, help='Rent rate')
def generate_lease_agreement(tid, lid, aid, fr, to, rent):
    apartments = pd.DataFrame(get_spreadsheet(config_parser.get('googledrive', 'apartments'), key, scope).get_all_records())
    tennants = pd.DataFrame(get_spreadsheet(config_parser.get('googledrive', 'tennants'), key, scope).get_all_records())
    landlords = pd.DataFrame(get_spreadsheet(config_parser.get('googledrive', 'landlords'), key, scope).get_all_records())

    details = build_details_dict(landlords.iloc[int(lid)], tennants.iloc[int(tid)], apartments.iloc[int(aid)], fr, to, rent)

    # print(landlords.iloc[int(lid)])
    # print(tennants.iloc[int(lid)])
    # print(apartments.iloc[int(lid)])

    prepare_agreement(details)

def build_details_dict(landlord, tennant, apartment, fr, to, rent):

    details = {
            "[1]":fr,
            "[2]": landlord.loc['Imię i nazwisko'],
            "[3]":landlord.loc['Ulica i numer domu'],
            "[4]":landlord.loc['Kod pocztowy'],
            "[5]":landlord.loc['Miasto'],
            "[6]":landlord.loc['Seria i numer dowodu osobistego'],
            "[7]":str(landlord.loc['Numer PESEL']),
            "[8]":tennant.loc['Imię i nazwisko'],
            "[9]":tennant.loc['Ulica i numer domu'],
            "[10]":tennant.loc['Kod pocztowy'],
            "[11]":tennant.loc['Miasto'],
            "[12]":tennant.loc['Seria i numer dowodu osobistego'],
            "[13]":str(tennant.loc['Numer PESEL']),
            "[14]":apartment.loc['Ulica i numer domu'],
            "[15]":str(apartment.loc['Powierzchnia']),
            "[16]":to,
            "[17]":str(rent),
            "[18]":apartment.loc['Miasto'],
            "[19]":tennant.loc['Adres email'],
            "[20]":landlord.loc['Adres email'],
            "[21]":str(tennant.loc['Numer telefonu']),
            "[22]":str(landlord.loc['Numer telefonu']),
            }

    return details

def prepare_agreement(details):
    # create appropriate files and copy template to dir
    path = config_parser.get('folders', 'agreements')+details['[8]'].replace(" ", "_")
    Path(path).mkdir(parents=True, exist_ok=True)
    filepath = path+'/'+details['[8]'].replace(" ", "_")+'.tex'
    copyfile('res/template.tex', filepath)

    # read copied template and substitute each placeholder with details
    for line in fileinput.input(filepath, inplace=1):
        line = line.rstrip()
        if not line:
            continue
        for f_key, f_value in details.items():
            if f_key in line:
                line = line.replace(f_key, f_value)
        print(line)

    # close file and compile pdf 
    fileinput.close()
    os.system("pdflatex -output-directory="+path+" "+filepath)
    print("Lease agreement generated under "+path+"/")
#-----------------------------------------------------
if __name__ == '__main__':
    cli()