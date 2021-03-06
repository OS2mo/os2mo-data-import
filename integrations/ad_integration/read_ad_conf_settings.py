import os
import json
import pathlib
import logging

logger = logging.getLogger("AdReader")

from integrations.ad_integration.utils import LazyDict
from exporters.utils.load_settings import load_settings


def _read_global_settings(top_settings):
    global_settings = {}

    global_settings['mora.base'] = top_settings.get('mora.base')
    global_settings['servers'] = top_settings.get('integrations.ad')[0].get('servers', [])
    global_settings['winrm_host'] = top_settings.get('integrations.ad.winrm_host')
    global_settings['system_user'] = top_settings['integrations.ad'][0]['system_user']
    global_settings['password'] = top_settings['integrations.ad'][0]['password']
    if not global_settings['winrm_host']:
        msg = 'Missing hostname for remote management server'
        logger.error(msg)
        raise Exception(msg)
    return global_settings


def _read_primary_ad_settings(top_settings, index=0):

    primary_settings = {}

    if top_settings.get('integrations.ad') is None:
        raise Exception("integration.ad settings not found")

    if len(top_settings['integrations.ad']) < (index + 1):
        raise Exception("ad index %d not found" % index)

    # settings that must be in place
    primary_settings['search_base'] = top_settings[
        'integrations.ad'][index].get("search_base")
    primary_settings['cpr_field'] = top_settings[
        'integrations.ad'][index].get("cpr_field")
    primary_settings['system_user'] = top_settings[
        'integrations.ad'][index].get("system_user")
    primary_settings['password'] = top_settings[
        'integrations.ad'][index].get('password')
    primary_settings['properties'] = top_settings[
        'integrations.ad'][index].get("properties")

    missing = []
    for key, val in primary_settings.items():
        if val is None:
            missing.append(key)

    # 36182 exclude non primary AD-users
    primary_settings["discriminator.field"] = top_settings[
        "integrations.ad"][index].get("discriminator.field")
    if primary_settings["discriminator.field"] is not None:

        # if we have a field we MUST have .values and .function
        primary_settings["discriminator.values"] = top_settings[
            "integrations.ad"][index].get("discriminator.values")
        if primary_settings["discriminator.values"] is None:
            missing.append("discriminator.values")

        primary_settings["discriminator.function"] = top_settings[
            "integrations.ad"][index].get("discriminator.function")
        if primary_settings["discriminator.function"] is None:
            missing.append("discriminator.function")

        if not primary_settings["discriminator.function"] in ["include", "exclude"]:
            raise ValueError("'ad.discriminator.function'" +
                " must be 'include' or 'exclude' for AD %d" % index
            )

    # Settings that do not need to be set, or have defaults
    #primary_settings['server'] = None
    primary_settings['servers'] = top_settings[
        'integrations.ad'][index].get('servers', [])
    primary_settings['caseless_samname'] = top_settings.get(
        'integrations.ad')[index].get('caseless_samname', True)
    primary_settings['sam_filter'] = top_settings.get(
        "integrations.ad")[index].get("sam_filter", '')
    primary_settings['cpr_separator'] = top_settings.get(
        'integrations.ad')[index].get('cpr_separator', '')
    primary_settings['ad_mo_sync_mapping'] = top_settings.get(
        'integrations.ad')[index].get('ad_mo_sync_mapping', {})
    primary_settings['method'] = top_settings[
        'integrations.ad'][index].get("method", "kerberos")

    # So far false in all known cases, default to false
    # get_ad_object = os.environ.get('AD_GET_AD_OBJECT', 'False')
    # primary_settings['get_ad_object'] = get_ad_object.lower() == 'true'
    primary_settings['get_ad_object'] = False

    if missing:
        msg = 'Missing settings in AD {}: {}'.format(index, missing)
        logger.error(msg)
        raise Exception(msg)

    return primary_settings


def _read_primary_write_information(top_settings):
    """
    Read the configuration for writing to the primary AD. If anything is missing,
    the AD write will be disabled.
    """
    # TODO: Some happy day, we could check for the actual validity of these
    primary_write_settings = {}

    # Shared with read
    primary_write_settings['cpr_field'] = top_settings.get(
        'integrations.ad')[0]['cpr_field']

    # Field for writing the uuid of a user, used to sync to STS
    primary_write_settings['uuid_field'] = top_settings.get(
        'integrations.ad.write.uuid_field')

    # Field for writing the name of the users level2orgunit (eg direktørområde)
    primary_write_settings['level2orgunit_field'] = top_settings.get(
        'integrations.ad.write.level2orgunit_field')

    # Field for the path to the users unit
    primary_write_settings['org_field'] = top_settings.get(
        'integrations.ad.write.org_unit_field')

    # Word to go after @ in UPN
    primary_write_settings['upn_end'] = top_settings.get(
        'integrations.ad.write.upn_end')

    # These are technically speaking not used in this context, but it is needed for
    # AD write and can benifit from the automated check.

    # UUID for the unit type considered to be level2orgunit
    primary_write_settings['level2orgunit_type'] = top_settings.get(
        'integrations.ad.write.level2orgunit_type'
    )

    missing = []

    for key, val in primary_write_settings.items():
        if val is None:
            missing.append(key)
    if len(missing) > 0:
        msg = 'Missing values for AD write {}'.format(missing)
        logger.info(msg)
        return {}

    # Template fields
    primary_write_settings['mo_to_ad_fields'] = top_settings.get(
        'integrations.ad_writer.mo_to_ad_fields', {}
    )
    primary_write_settings['template_to_ad_fields'] = top_settings.get(
        'integrations.ad_writer.template_to_ad_fields', {}
    )

    # Check for illegal configuration of AD Write.
    mo_to_ad_fields = primary_write_settings['mo_to_ad_fields']
    template_to_ad_fields = primary_write_settings['template_to_ad_fields']
    ad_field_names = (
        list(mo_to_ad_fields.values()) +
        list(template_to_ad_fields.keys()) + [
            primary_write_settings['org_field'],
            primary_write_settings['level2orgunit_field'],
            primary_write_settings['uuid_field']
        ]
    )
    # Conflicts are case-insensitive
    ad_field_names = list(map(lambda ad_field: ad_field.lower(), ad_field_names))
    if len(ad_field_names) > len(set(ad_field_names)):
        msg = 'Duplicate AD fieldnames in settings: {}'
        logger.info(msg.format(sorted(ad_field_names)))
        primary_write_settings = {}

    return primary_write_settings


def _NEVER_read_school_ad_settings():
    raise RuntimeError("NEVER call this - it is obsolete")
    school_settings = {}

    school_settings['search_base'] = os.environ.get('AD_SCHOOL_SEARCH_BASE')
    school_settings['cpr_field'] = os.environ.get('AD_SCHOOL_CPR_FIELD')
    school_settings['system_user'] = os.environ.get('AD_SCHOOL_SYSTEM_USER')
    school_settings['password'] = os.environ.get('AD_SCHOOL_PASSWORD')
    ad_school_prop_raw = os.environ.get('AD_SCHOOL_PROPERTIES')
    if ad_school_prop_raw:
        school_settings['properties'] = set(ad_school_prop_raw.split(' '))
    else:
        school_settings['properties'] = None

    missing = []
    for key, val in school_settings.items():
        if not val:
            missing.append(key)
    if missing:
        msg = 'Missing values for {}, skipping school AD'.format(missing)
        logger.info(msg)
        school_settings['read_school'] = False
    else:
        school_settings['read_school'] = True

    # Settings that do not need to be set
    school_settings['server'] = os.environ.get('AD_SCHOOL_SERVER')
    school_settings['cpr_separator'] = top_settings.get(
        'integrations.ad.school_cpr_separator', '')

    # So far true in all known cases, default to true
    get_ad_object = os.environ.get('AD_SCHOOL_GET_AD_OBJECT', 'True')
    school_settings['get_ad_object'] = get_ad_object.lower() == 'true'

    return school_settings


SETTINGS = LazyDict()
SETTINGS.set_initializer(load_settings)


def read_settings(top_settings=SETTINGS, index=0):
    settings = {}
    settings['global'] = _read_global_settings(top_settings)
    settings['primary'] = _read_primary_ad_settings(top_settings, index)
    settings['primary_write'] = _read_primary_write_information(top_settings)
    return settings


if __name__ == '__main__':
    read_settings()
