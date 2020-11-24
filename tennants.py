#   Copyright (c) Jarosław Mirek
import os
import sys
import logging
from pathlib import Path
from shutil import copyfile
import fileinput
import numpy as np
import click
import pandas as pd
import gsshandler
from scrape import get_smpiast_costs, get_pgnig_costs, get_tauron_costs

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
    data = pd.DataFrame(gsshandler.get_spreadsheet('landlords').get_all_records())
    print(data)

@cli.command('lst', help='List all tennants')
def list_all_tennants():
    data = pd.DataFrame(gsshandler.get_spreadsheet('tennants').get_all_records())
    print(data)

@cli.command('lsa', help='List all apartments')
def list_all_apartments():
    data = pd.DataFrame(gsshandler.get_spreadsheet('apartments').get_all_records())
    print(data)

@cli.command('genbil', help='Generate bills for the current period for a particular tennant')
@click.option('--aid', required=True, help='Apartment ID')
@click.option('--month', multiple=True, required=True,
              help='For which months bills should be generated')
@click.option('--year', required=True, help='For which year bills should be generated')
def generate_bills(aid, month, year):
    months = list(month)
    water = get_smpiast_costs(aid, months, year)
    electricity = get_tauron_costs(aid, months, year)
    gas = get_pgnig_costs(months, year)
    tennants = pd.DataFrame(gsshandler.get_spreadsheet('tennants').get_all_records())
    no_of_tennants = len(tennants[tennants['ID mieszkania'] == int(aid)])
    print(no_of_tennants)


    tmp_bills = pd.merge(water.assign(grouper=water['data'].dt.to_period('M')),
                         gas.assign(grouper=gas['data'].dt.to_period('M')),
                         how='left', on='grouper')
    bills = pd.merge(tmp_bills.assign(grouper=tmp_bills['data_x'].dt.to_period('M')),
                     electricity.assign(grouper=electricity['data'].dt.to_period('M')),
                     how='left', on='grouper')
    bills = bills.rename(columns={'data_x':'Data', 'zimna':'Woda zimna', 'ciepla':'Woda ciepła',
                                  'kwota_y':'Energia elektryczna', 'kwota_x':'Gaz'})
    bills['Internet'] = np.nan
    bills['Internet'] = pd.to_numeric(bills['Internet'])
    bills.drop(['data', 'grouper', 'data_y'], inplace=True, axis=1)
    bills.fillna(value=0, inplace=True)
    bills['Razem wszystkie opłaty'] = (bills['Energia elektryczna'] \
        + bills['Gaz'] + bills['Woda ciepła'] + bills['Woda zimna'] \
        + bills['Internet']).round(decimals=2)
    bills['Razem na jedną osobę'] = (bills['Razem wszystkie opłaty'] \
        /no_of_tennants).round(decimals=2)

    #print(bills)
    path = gsshandler.get_folder('bills')
    Path(path).mkdir(parents=True, exist_ok=True)
    bills.to_csv(path + aid +'_'+ str(months) + '_' + year + '.csv')

def send_bills():
    pass

def send_agreement():
    pass

@cli.command('genagr', help='Generate lease agreement for a particular tennant')
@click.option('--tid', required=True, help='Tennant ID')
@click.option('--lid', required=True, help='Landlord ID')
@click.option('--aid', required=True, help='Apartment ID')
@click.option('--dfrom', '-fr', required=True, help='From date')
@click.option('--dto', '-to', required=True, help="To date")
@click.option('--rent', required=True, help='Rent rate')
def generate_lease_agreement(tid, lid, aid, dfrom, dto, rent):
    apartments = pd.DataFrame(gsshandler.get_spreadsheet('apartments').get_all_records())
    tennants = pd.DataFrame(gsshandler.get_spreadsheet('tennants').get_all_records())
    landlords = pd.DataFrame(gsshandler.get_spreadsheet('landlords').get_all_records())

    details = build_details_dict(landlords.iloc[int(lid)],
                                 tennants.iloc[int(tid)],
                                 apartments[apartments['ID mieszkania'] == int(aid)].iloc[0],
                                 dfrom, dto, rent)

    prepare_agreement(details)

def build_details_dict(landlord, tennant, apartment, dfrom, dto, rent):

    details = {
        "[1]":dfrom,
        "[2]":landlord.loc['Imię i nazwisko'],
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
        "[16]":dto,
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
    path = gsshandler.get_folder('agreements')+details['[8]'].replace(" ", "_")
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
