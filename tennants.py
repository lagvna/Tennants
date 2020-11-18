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

import mechanize
import http.cookiejar
from bs4 import BeautifulSoup
import html2text

key = '/home/lagvna/client_secret.json'
scope = ['https://www.googleapis.com/auth/drive']

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
    data = pd.DataFrame(get_spreadsheet("Wlasciciele", key, scope).get_all_records())
    print(data)

@cli.command('lst', help='List all tennants')
def list_all_tennants():
    data = pd.DataFrame(get_spreadsheet("Umowa najmu (Odpowiedzi)", key, scope).get_all_records())
    print(data)

@cli.command('lsa', help='List all apartments')
def list_all_apartments():
    data = pd.DataFrame(get_spreadsheet("Mieszkania", key, scope).get_all_records())
    print(data)

@cli.command('genbil', help='Generate bills for the current period for a particular tennant')
# @click.option('--tid', required=True, help='Tennant ID')
# @click.option('--month', required=True, help='For which month bills should be generated')
# @click.option('--year', required=True, help='For which year bills should be generated')
def generate_bills():
    pass

@cli.command('genagr', help='Generate lease agreement for a particular tennant')
@click.option('--tid', required=True, help='Tennant ID')
@click.option('--lid', required=True, help='Landlord ID')
@click.option('--aid', required=True, help='Apartment ID')
@click.option('--fr', required=True, help='From date')
@click.option('--to', required=True, help="To date")
@click.option('--rent', required=True, help='Rent rate')
def generate_lease_agreement(tid, lid, aid, fr, to, rent):
    apartments = pd.DataFrame(get_spreadsheet("Mieszkania", key, scope).get_all_records())
    tennants = pd.DataFrame(get_spreadsheet("Umowa najmu (Odpowiedzi)", key, scope).get_all_records())
    landlords = pd.DataFrame(get_spreadsheet("Wlasciciele", key, scope).get_all_records())

    details = build_details_dict(landlords.iloc[int(lid)], tennants.iloc[int(tid)], apartments.iloc[int(aid)], fr, to, rent)

    # print(landlords.iloc[int(lid)])
    # print(tennants.iloc[int(lid)])
    # print(apartments.iloc[int(lid)])

    prepare_agreement(details)

def build_details_dict(landlord, tennant, apartment, fr, to, rent):

    details = {"[1]":fr,"[2]": landlord.loc['Imię i nazwisko'],
            "[3]":landlord.loc['Ulica i numer domu'], "[4]":landlord.loc['Kod pocztowy'],
            "[5]":landlord.loc['Miasto'], "[6]":landlord.loc['Seria i numer dowodu osobistego'],
            "[7]":str(landlord.loc['Numer PESEL']), "[8]":tennant.loc['Imię i nazwisko'],
            "[9]":tennant.loc['Ulica i numer domu'], "[10]":tennant.loc['Kod pocztowy'],
            "[11]":tennant.loc['Miasto'], "[12]":tennant.loc['Seria i numer dowodu osobistego'],
            "[13]":str(tennant.loc['Numer PESEL']),"[14]":apartment.loc['Ulica i numer domu'],
            "[15]":str(apartment.loc['Powierzchnia']), "[16]":to,
            "[17]":str(rent), "[19]":tennant.loc['Adres email'],
            "[20]":landlord.loc['Adres email'], "[21]":str(tennant.loc['Numer telefonu']),
            "[22]":str(landlord.loc['Numer telefonu']),
            "[18]":apartment.loc['Miasto']}

    print(details)

    return details

def prepare_agreement(details):
    path = '/home/lagvna/Tennants/res/umowy/'+details['[8]']
    Path(path).mkdir(parents=True, exist_ok=True)
    filepath = path+'/'+details['[8]']+'.tex'
    copyfile('res/template.tex', filepath)

    for line in fileinput.input(filepath, inplace=1):
        line = line.rstrip()
        if not line:
            continue
        for f_key, f_value in details.items():
            if f_key in line:
                line = line.replace(f_key, f_value)
        print(line)

# @cli.command('loadkey', help='Provide path to Google authentication key')
# @click.option('--dir', required=True, help='Provide path to authentication key')
# def load_key():
#     pass

# @cli.command('mkl', help='Add new landlord')
# @click.option('--name', required=True, help='Name and surname')
# @click.option('--idno', required=True, help='Personal ID card number')
# @click.option('--pesel', required=True, help='PESEL number')
# @click.option('--address', required=True, help="Landlord's permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', required=True, help='Town and zipcode')
# def add_landlord():
#     pass

# @cli.command('rml', help='Remove landlord')
# @click.option('--id', required=True, help='Landlord ID')
# @click.option('--name', help='Name and surname')
# @click.option('--idno', help='Personal ID card number')
# @click.option('--pesel', help='PESEL number')
# @click.option('--address', help="Landlord's permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', help='Town and zipcode')
# def remove_landlord():
#     pass

# @cli.command('modl', help='Modify properties of landlord')
# @click.option('--id', required=True, help='Landlord ID')
# @click.option('--name', help='Name and surname')
# @click.option('--idno', help='Personal ID card number')
# @click.option('--pesel', help='PESEL number')
# @click.option('--address', help="Landlord's permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', help='Town and zipcode')
# def modify_landlord():
#     pass

# @cli.command('mkt', help='Add new tennant')
# @click.option('--name', required=True, help='Name and surname')
# @click.option('--idno', required=True, help='Personal ID card number')
# @click.option('--pesel', required=True, help='PESEL number')
# @click.option('--address', required=True, help="Tennant's permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', required=True, help='Town and zipcode')
# def add_tennant():
#     pass

# @cli.command('rmt', help='Remove tennant')
# @click.option('--id', required=True, help='Tennant ID')
# @click.option('--name', help='Name and surname')
# @click.option('--idno', help='Personal ID card number')
# @click.option('--pesel', help='PESEL number')
# @click.option('--address', help="Tennant's permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', help='Town and zipcode')
# def remove_tennant():
#     pass

# @cli.command('modt', help='Modify properties of a tennant')
# @click.option('--id', required=True, help='Tennant ID')
# @click.option('--name', help='Name and surname')
# @click.option('--idno', help='Personal ID card number')
# @click.option('--pesel', help='PESEL number')
# @click.option('--address', help="Tennant's permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', help='Town and zipcode')
# def modify_tennant():
#     pass

# @cli.command('mka', help='Add new apartment')
# @click.option('--address', required=True, help="Tennants permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', required = True, help='Town and zipcode')
# @click.option('--landlord', required = True, help='Apartment owner')
# def add_apartment():
#     pass

# @cli.command('rma', help='Remove aparment')
# @click.option('--id', required=True, help='Apartment ID')
# @click.option('--address', help="Tennants permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', help='Town and zipcode')
# @click.option('--landlord', help='Apartment owner')
# def remove_apartment():
#     pass

# @cli.command('moda', help='Modify properties of an apartment')
# @click.option('--id', required=True, help='Apartment ID')
# @click.option('--address', help="Tennants permanent address"
#                                                 "(street and house number only)")
# @click.option('--town', help='Town and zipcode')
# @click.option('--landlord', help='Apartment owner')
# def modify_apartment():
#     pass


#-----------------------------------------------------
if __name__ == '__main__':
    cli()