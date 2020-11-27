""" This is a CLI module for tennants application, allowing to execute particular functions
    with commands typed in terminal.
"""

#   Copyright (c) Jarosław Mirek
import logging
from logging import StreamHandler
from pathlib import Path
import click
import pandas as pd
from Tennants.confighandler import get_folder
from Tennants.gsshandler import get_spreadsheet
from Tennants import agreementhandler
from Tennants.billshandler import BillsHandler

root_logger = logging.getLogger()

@click.group()
@click.option('--quiet', default=False, is_flag=True, help='Run in silent mode')
def cli(quiet):
    """
    tennaants is a command line program which facilitates the management of renting apartments.
    It allows to manage tennants, apartments, generate lease agreements and calculate bills
    from SM Piast Wroclaw, Tauron and PGNiG. It operates on documents held on Google Drive.
    """
    console_handler = StreamHandler()

    if quiet:
        root_logger.setLevel(logging.ERROR)
        console_handler.setLevel(logging.ERROR)

    else:
        root_logger.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)
    logger_formatter = logging.Formatter('%(asctime)s: %(name)s - %(levelname)s - %(message)s',
                                         datefmt='%y-%m-%d %H:%M:%S',)
    console_handler.setFormatter(logger_formatter)
    root_logger.addHandler(console_handler)

@cli.command('lsl', help='List all landlords')
def list_all_landlords():
    """ List all landlords """
    data = pd.DataFrame(get_spreadsheet('landlords').get_all_records())
    print(data)

@cli.command('lst', help='List all tennants')
def list_all_tennants():
    """ List all tennants """
    data = pd.DataFrame(get_spreadsheet('tennants').get_all_records())
    print(data)

@cli.command('lsa', help='List all apartments')
def list_all_apartments():
    """ List all apartments """
    data = pd.DataFrame(get_spreadsheet('apartments').get_all_records())
    print(data)

@cli.command('genbil', help='Generate bills for the current period for a particular tennant')
@click.option('--aid', required=True, help='Apartment ID')
@click.option('--month', multiple=True, required=True,
              help='For which months bills should be generated')
@click.option('--year', required=True, help='For which year bills should be generated')
def generate_bills(aid, month, year):
    """ Generate bills for specified months and year for a particular apartment."""
    months = list(month)
    bills_handler = BillsHandler(aid, months, year)
    bills = bills_handler.calculate_bills()

    print(bills)

    path = str(get_folder('bills'))
    Path(path).mkdir(parents=True, exist_ok=True)
    bills.to_csv(path + aid +'_'+ str(months) + '_' + year + '.csv')

    root_logger.info('Bills saved under '+path+ aid +'_'+ str(months) + '_' + year + '.csv')

def send_bills():
    """ Send bills to tennants """
    pass

def send_agreement():
    """ Send agreement to tennant """
    pass

@cli.command('genagr', help='Generate lease agreement for a particular tennant')
@click.option('--tid', required=True, help='Tennant ID')
@click.option('--lid', required=True, help='Landlord ID')
@click.option('--aid', required=True, help='Apartment ID')
@click.option('--dfrom', '-fr', required=True, help='From date')
@click.option('--dto', '-to', required=True, help="To date")
@click.option('--rent', required=True, help='Rent rate')
def generate_lease_agreement(tid, lid, aid, dfrom, dto, rent):
    """ Generate lease agreement for specified tennant, landlord and aparment."""

    agreementhandler.prepare_agreement(tid, lid, aid, dfrom, dto, rent)

#-----------------------------------------------------
if __name__ == '__main__':
    cli()
