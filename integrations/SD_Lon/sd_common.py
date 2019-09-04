import os
import pickle
import logging
import hashlib
import requests
import xmltodict
from pathlib import Path
logger = logging.getLogger("sdCommon")

INSTITUTION_IDENTIFIER = os.environ.get('INSTITUTION_IDENTIFIER')
SD_USER = os.environ.get('SD_USER', None)
SD_PASSWORD = os.environ.get('SD_PASSWORD', None)
if not (INSTITUTION_IDENTIFIER and SD_USER and SD_PASSWORD):
    raise Exception('Credentials missing')


def sd_lookup(url, params={}):
    logger.info('Retrive: {}'.format(url))
    logger.debug('Params: {}'.format(params))

    BASE_URL = 'https://service.sd.dk/sdws/'
    full_url = BASE_URL + url

    payload = {
        'InstitutionIdentifier': INSTITUTION_IDENTIFIER,
    }
    payload.update(params)
    m = hashlib.sha256()

    keys = sorted(payload.keys())
    for key in keys:
        m.update((str(key) + str(payload[key])).encode())
    m.update(full_url.encode())
    lookup_id = m.hexdigest()
    cache_file = Path('sd_' + lookup_id + '.p')

    if cache_file.is_file():
        with open(str(cache_file), 'rb') as f:
            response = pickle.load(f)
        logger.info('This SD lookup was found in cache: {}'.format(lookup_id))
    else:
        response = requests.get(
            full_url,
            params=payload,
            auth=(SD_USER, SD_PASSWORD)
        )
        with open(str(cache_file), 'wb') as f:
            pickle.dump(response, f, pickle.HIGHEST_PROTOCOL)

    dict_response = xmltodict.parse(response.text)
    if url in dict_response:
        xml_response = dict_response[url]
    else:
        logger.error('Envelope: {}'.format(dict_response['Envelope']))
        xml_response = {}
    logger.debug('Done with {}'.format(url))
    return xml_response


def calc_employment_id(employment):
    employment_id = employment['EmploymentIdentifier']
    try:
        employment_number = int(employment_id)
    except ValueError:  # Job id is not a number?
        employment_number = 999999

    employment_id = {
        'id': employment_id,
        'value': employment_number
    }
    return employment_id