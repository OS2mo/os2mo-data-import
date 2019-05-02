import os
import sys
import datetime

from os2mo_data_import import ImportHelper
sys.path.append('..')
import sd_importer

MUNICIPALTY_NAME = os.environ.get('MUNICIPALITY_NAME', 'SD-Løn Import')
MUNICIPALTY_CODE = os.environ.get('MUNICIPALITY_CODE', 0)
MOX_BASE = os.environ.get('MOX_BASE', 'http://localhost:8080')
MORA_BASE = os.environ.get('MORA_BASE', 'http://localhost:80')

GLOBAL_GET_DATE = datetime.datetime(2019, 4, 1, 0, 0)
GLOBAL_TO = None

importer = ImportHelper(
    create_defaults=True,
    mox_base=MOX_BASE,
    mora_base=MORA_BASE,
    system_name='SD-Import',
    end_marker='SDSTOP',
    store_integration_data=True
)

sd = sd_importer.SdImport(
    importer,
    MUNICIPALTY_NAME,
    MUNICIPALTY_CODE,
    import_date_from=GLOBAL_GET_DATE,
    import_date_to = GLOBAL_TO,
)

sd.create_ou_tree()
sd.create_employees()

importer.import_all()

