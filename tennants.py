#   Copyright (c) Jarosław Mirek
import sys
import logging
from pathlib import Path
import click
import pandas as pd
import confighandler
import gsshandler
import agreementhandler
from billshandler import BillsHandler

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
    bills_handler = BillsHandler(aid, months, year)
    bills = bills_handler.calculate_bills()

    print(bills)

    path = str(confighandler.get_folder('bills'))
    Path(path).mkdir(parents=True, exist_ok=True)
    bills.to_csv(path + aid +'_'+ str(months) + '_' + year + '.csv')

    logging.info('Bills saved under '+path + aid +'_'+ str(months) + '_' + year + '.csv')

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
    agreementhandler.prepare_agreement(tid, lid, aid, dfrom, dto, rent)

#-----------------------------------------------------
if __name__ == '__main__':
    cli()
