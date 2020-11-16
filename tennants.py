#	Copyright (c) Jarosław Mirek


import os
import sys
import logging
import click
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

@click.group()
@click.option('--quiet', default=False, is_flag=True, help='Run in silent mode')
def cli(quiet):
    """
    tennaants is a command line program which facilitates the management of renting apartments.
    It allows to manage tennants, apartments, generate lease agreements and calculate bills
    for the current period. It operates on documents held on Google Drive.
    """
    if quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@cli.command('mkl', help='Add new landlord')
@click.option('--name', required=True, help='Name and surname')
@click.option('--idno', required=True, help='Personal ID card number')
@click.option('--pesel', required=True, help='PESEL number')
@click.option('--address', required=True, help="Landlord's permanent address"
			  									"(street and house number only)")
@click.option('--town', required=True, help='Town and zipcode')
def add_landlord():
	pass

@cli.command('rml', help='Remove landlord')
@click.option('--id', required=True, help='Landlord ID')
@click.option('--name', help='Name and surname')
@click.option('--idno', help='Personal ID card number')
@click.option('--pesel', help='PESEL number')
@click.option('--address', help="Landlord's permanent address"
			  									"(street and house number only)")
@click.option('--town', help='Town and zipcode')
def remove_landlord():
	pass

@cli.command('modl', help='Modify properties of landlord')
@click.option('--id', required=True, help='Landlord ID')
@click.option('--name', help='Name and surname')
@click.option('--idno', help='Personal ID card number')
@click.option('--pesel', help='PESEL number')
@click.option('--address', help="Landlord's permanent address"
			  									"(street and house number only)")
@click.option('--town', help='Town and zipcode')
def modify_landlord():
	pass

@cli.command('lsl', help='List all landlords')
def list_all_landlords():
	scope = ['https://spreadsheets.google.com/feeds',
			'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('/home/lagvna/client_secret.json', scope)
	client = gspread.authorize(creds)

	sheet = client.open("Wlasciciele").sheet1

	data = pd.DataFrame(sheet.get_all_records())
	print(data.head())

@cli.command('mkt', help='Add new tennant')
@click.option('--name', required=True, help='Name and surname')
@click.option('--idno', required=True, help='Personal ID card number')
@click.option('--pesel', required=True, help='PESEL number')
@click.option('--address', required=True, help="Tennant's permanent address"
			  									"(street and house number only)")
@click.option('--town', required=True, help='Town and zipcode')
def add_tennant():
	pass

@cli.command('rmt', help='Remove tennant')
@click.option('--id', required=True, help='Tennant ID')
@click.option('--name', help='Name and surname')
@click.option('--idno', help='Personal ID card number')
@click.option('--pesel', help='PESEL number')
@click.option('--address', help="Tennant's permanent address"
			  									"(street and house number only)")
@click.option('--town', help='Town and zipcode')
def remove_tennant():
	pass

@cli.command('modt', help='Modify properties of a tennant')
@click.option('--id', required=True, help='Tennant ID')
@click.option('--name', help='Name and surname')
@click.option('--idno', help='Personal ID card number')
@click.option('--pesel', help='PESEL number')
@click.option('--address', help="Tennant's permanent address"
			  									"(street and house number only)")
@click.option('--town', help='Town and zipcode')
def modify_tennant():
	pass

@cli.command('lst', help='List all tennants')
def list_all_tennants():
	scope = ['https://spreadsheets.google.com/feeds',
			'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('/home/lagvna/client_secret.json', scope)
	client = gspread.authorize(creds)

	sheet = client.open("Umowa najmu (Odpowiedzi)").sheet1

	data = pd.DataFrame(sheet.get_all_records())
	print(data.head())

@cli.command('mka', help='Add new apartment')
@click.option('--address', required=True, help="Tennants permanent address"
			  									"(street and house number only)")
@click.option('--town', required = True, help='Town and zipcode')
@click.option('--landlord', required = True, help='Apartment owner')
def add_apartment():
	pass

@cli.command('rma', help='Remove aparment')
@click.option('--id', required=True, help='Apartment ID')
@click.option('--address', help="Tennants permanent address"
			  									"(street and house number only)")
@click.option('--town', help='Town and zipcode')
@click.option('--landlord', help='Apartment owner')
def remove_apartment():
	pass

@cli.command('moda', help='Modify properties of an apartment')
@click.option('--id', required=True, help='Apartment ID')
@click.option('--address', help="Tennants permanent address"
			  									"(street and house number only)")
@click.option('--town', help='Town and zipcode')
@click.option('--landlord', help='Apartment owner')
def modify_apartment():
	pass

@cli.command('lsa', help='List all apartments')
def list_all_tennants():
	scope = ['https://spreadsheets.google.com/feeds',
			'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('/home/lagvna/client_secret.json', scope)
	client = gspread.authorize(creds)

	sheet = client.open("Mieszkania").sheet1

	data = pd.DataFrame(sheet.get_all_records())
	print(data.head())

@cli.command('genbil', help='Generate bills for the current period for a particular tennant')
@click.option('--tid', required=True, help='Tennant ID')
@click.option('--month', required=True, help='For which month bills should be generated')
@click.option('--year', required=True, help='For which year bills should be generated')
def generate_bills():
	pass

@cli.command('genagr', help='Generate lease agreement for a particular tennant')
@click.option('--tid', required=True, help='Tennant ID')
@click.option('--aid', required=True, help='Apartment ID')
@click.option('--from', required=True, help='From date')
@click.option('--to', required=True, help="To date")
@click.option('--rent', required=True, help='Rent rate')
def generate_lease_agreement():
	pass

@cli.command('loadkey', help='Provide path to Google authentication key')
@click.option('--dir', required=True, help='Provide path to authentication key')
def load_key():
	pass


#-----------------------------------------------------
if __name__ == '__main__':
    cli()