import json
from collections import ChainMap
from datetime import date, timedelta
from functools import partial
from operator import attrgetter

from exporters.sql_export.lc_for_jobs_db import get_engine
from exporters.sql_export.sql_table_defs import ItForbindelse
from os2mo_helpers.mora_helpers import MoraHelper
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

#This will find and terminate any dublicate it systems associated with users.
#It searches the actual-state database, so be sure to run lc_for_jobs first.

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


def main():
    engine = get_engine()

    # Prepare session
    Session = sessionmaker(bind=engine, autoflush=False)
    session = Session()

    # List of tuples, it_sys_uuid, bruger_uuid, enhed_uuid, brugernavn, count
    duplicates = find_duplicate_it_connections(session)
    # List of dicts from id --> uuid (for rows to be deleted)
    duplicate_maps = map(partial(construct_duplicate_dict, session), duplicates)
    # One combined dict from id --> uuid (for rows to be deleted)
    output = dict(ChainMap(*duplicate_maps))

    # Output delete-map
    print(json.dumps(output, indent=4, sort_keys=True))

    #Terminate dublicate IT systems in MO by setting validity to yesterday.
    helper = MoraHelper(hostname="http://localhost:5000",use_cache=False)
    yesterday = date.today() - timedelta(days=1)
    counter = 0
    max_dup = max(output.keys())
    for uuid in output.values():
        counter += 1
        payload = {
             'type': 'it',
             'uuid': uuid,
             'validity': {
                 'to': yesterday.strftime("%Y-%m-%d")
             }
             }
    
        response = helper._mo_post('details/terminate', payload)
        response.raise_for_status()
        print("{}/{} duplicate it systems deleted".format(counter, max_dup))
    print("{} duplicate it systems deleted".format(counter))

if __name__ == "__main__":
    main()
