import requests
import csv
import pandas as pd

MAPPING_FILE = ''
XLSX_FILE = ''


def get_mo_users():
    r = requests.get('https://os2moprod.rebild.dk/service/o/ab08933c-45a6-4b32-b131-581cd33e6056/e/')
    r.raise_for_status()
    return r.json()


def get_csv_mapping():
    with open(MAPPING_FILE, 'r') as f:
        csv_reader = csv.DictReader(f, delimiter=";")
        mapping = {
            line["mo_uuid"]: line["ad_guid"]
            for line in csv_reader
        }
    return mapping


def get_xlsx_users():
    with pd.ExcelFile(XLSX_FILE) as xlsx_file:
        sheet = xlsx_file.parse('Rettighedstildelinger')
        xlsx_users = {row.Bruger for row in sheet.iterrows()}
    return xlsx_users


def main():
    mo_users = get_mo_users()
    mapping = get_csv_mapping()
    xlsx_users = get_xlsx_users()












if __name__ == '__main__':
    main()
