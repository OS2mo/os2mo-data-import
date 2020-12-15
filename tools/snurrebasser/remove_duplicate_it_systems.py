import json
from collections import ChainMap

import requests
from functools import partial
from operator import attrgetter

from exporters.sql_export.lc_for_jobs_db import get_engine
from exporters.sql_export.sql_table_defs import ItForbindelse
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker


def find_duplicate_it_connections(session):
    # These columns specify uniqueness
    unique_columns = (
        ItForbindelse.it_system_uuid,
        ItForbindelse.bruger_uuid,
        ItForbindelse.enhed_uuid,
        ItForbindelse.brugernavn,
    )
    return (
        session.query(*unique_columns, func.count(ItForbindelse.id))
        .group_by(*unique_columns)
        .having(func.count(ItForbindelse.id) > 1)
        .all()
    )


def find_duplicate_rows(session, duplicate_entry):
    # Unpack row, corresponds to find_duplicate_it_connections select
    it_system_uuid, bruger_uuid, enhed_uuid, brugernavn, _ = duplicate_entry
    # Find duplicate rows by filtering on the duplicated values
    return (
        session.query(ItForbindelse)
        .filter(
            ItForbindelse.it_system_uuid == it_system_uuid,
            ItForbindelse.bruger_uuid == bruger_uuid,
            ItForbindelse.enhed_uuid == enhed_uuid,
            ItForbindelse.brugernavn == brugernavn,
        )
        .order_by(ItForbindelse.startdato)
        .all()
    )


def construct_duplicate_dict(session, duplicate_entry):
    duplicate_rows = find_duplicate_rows(session, duplicate_entry)
    # Remove all but newest entry, as we want to keep 1
    duplicate_rows = duplicate_rows[:-1]
    # Build dict from id --> uuid for all other rows
    row_dict = dict(map(attrgetter("id", "uuid"), duplicate_rows))
    return row_dict


def get_addresses_for(uuids):
    addresses = []
    for uuid in uuids:
        r = requests.get( 'http://localhost:8080/organisation/organisationfunktion?tilknyttedeitsystemer={}'.format(uuid))
        r.raise_for_status()
        addresses.append(r.json()['results'][0])
    return addresses


def main():
    engine = get_engine()

    from more_itertools import flatten
    uuids = ["16a21bd1-6669-4270-a65f-6e7612c08f41"]
    addresses = list(flatten(get_addresses_for(uuids)))
    
    print(len(addresses))
    
    delete_from_lora(addresses)

def delete_from_lora(duplicate_dict):

    for uuid in duplicate_dict:
        r = requests.delete('http://localhost:8080/organisation/organisationfunktion/{}'.format(uuid))
        r.raise_for_status()
        print(uuid)


if __name__ == "__main__":
    main()
