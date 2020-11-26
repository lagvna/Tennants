import os
import logging
from pathlib import Path
from shutil import copyfile
import fileinput
import pandas as pd
import confighandler
import gsshandler


def build_details_dict(tennant, landlord, apartment, dfrom, dto, rent):

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
        "[22]":str(landlord.loc['Numer telefonu'])
        }

    return details

def get_data(tid, lid, aid, dfrom, dto, rent):

    apartments = pd.DataFrame(gsshandler.get_spreadsheet('apartments').get_all_records())
    tennants = pd.DataFrame(gsshandler.get_spreadsheet('tennants').get_all_records())
    landlords = pd.DataFrame(gsshandler.get_spreadsheet('landlords').get_all_records())

    print(apartments)
    print(tennants)
    print(landlords)

    details = build_details_dict(tennants.iloc[int(tid)],
                                 landlords.iloc[int(lid)],
                                 apartments[apartments['ID mieszkania'] == int(aid)].iloc[0],
                                 dfrom, dto, rent)

    return details

def prepare_agreement(tennant, landlord, apartment, dfrom, dto, rent):
    details = get_data(landlord, tennant, apartment, dfrom, dto, rent)

    # create appropriate files and copy template to dir
    path = confighandler.get_folder('agreements')+details['[8]'].replace(" ", "_")
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
    logging.info("Lease agreement generated under "+path+"/")
