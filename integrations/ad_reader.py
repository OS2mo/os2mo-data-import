import os
import json
import pickle
import logging
import hashlib
from pathlib import Path
from winrm import Session

logger = logging.getLogger("AdReader")

WINRM_HOST = os.environ.get('WINRM_HOST', None)
AD_SYSTEM_USER = os.environ.get('AD_SYSTEM_USER', None)
AD_PASSWORD = os.environ.get('AD_PASSWORD', None)
SCHOOL_AD_SYSTEM_USER = os.environ.get('SCHOOL_AD_SYSTEM_USER', None)
SCHOOL_AD_PASSWORD = os.environ.get('SCHOOL_AD_PASSWORD', None)
# SEARCH_BASE
# PROPERTIES
# SKIP_BRUGERTYPE


class ADParameterReader(object):

    def __init__(self):
        if WINRM_HOST:
            self.session = Session(
                'http://{}:5985/wsman'.format(WINRM_HOST),
                transport='kerberos',
                auth=(None, None)
            )
        else:
            self.session = None
        self.results = {}

    def _run_ps_script(self, ps_script):
        """
        Run a power shell script and return the result. If it fails, the
        error is returned in its raw form.
        :param ps_script: The power shell script to run.
        :return: A dictionary with the returned parameters.
        """
        response = {}
        if not self.session:
            return response
        r = self.session.run_ps(ps_script)
        if r.status_code == 0:
            if r.std_out:
                response = json.loads(r.std_out.decode('Latin-1'))
        else:
            response = r.std_err
        return response

    def _build_user_credential(self, school=False):
        """
        Build the commonn set of Power Shell commands that is needed to
        run the AD commands.
        :return: A suitable string to prepend to AD commands.
        """
        credential_template = """
        $User = "{}"
        $PWord = ConvertTo-SecureString –String "{}" –AsPlainText -Force
        $TypeName = "System.Management.Automation.PSCredential"
        $UserCredential = New-Object –TypeName $TypeName –ArgumentList $User, $PWord
        """
        if not school:
            user_credential = credential_template.format(AD_SYSTEM_USER, AD_PASSWORD)
        else:
            user_credential = credential_template.format(SCHOOL_AD_SYSTEM_USER,
                                                         SCHOOL_AD_PASSWORD)
        return user_credential

    def read_encoding(self):
        """
        Read the character encoding of the Power Shell session.
        """
        ps_script = "$OutputEncoding | ConvertTo-Json"
        response = self._run_ps_script(ps_script)
        return response

    def _get_from_ad(self, user=None, cpr=None, school=False):
        """
        Read all properties of an AD user. The user can be retrived either by cpr
        or by AD user name.
        :param user: The AD username to retrive.
        :param cpr: cpr number of the user to retrive.
        :return: All properties listed in AD for the user.
        """
        if user:
            dict_key = user
            ps_template = "get-aduser {} "
            get_command = ps_template.format(user)

        if cpr:
            dict_key = cpr
            # Here we should strongly consider to strip part of the cpr to
            # get more users at the same time to increase performance.
            # Lookup time is only very slightly dependant on the number
            # of results.
            ps_template = "get-aduser -Filter 'xAttrCPR -like \"{}\"'"

        get_command = ps_template.format(dict_key)

        if school:
            search_base = ('-Server uv-viborg.local ' +
                           '-SearchBase "DC=uv-viborg,DC=local" ')
        else:
            search_base = ' -SearchBase "OU=Kommune,DC=viborg,DC=local" '

        credentials = ' -Credential $usercredential'
        if school:
            properties = (' | Get-ADObject -Properties xAttrCPR,ObjectGuid,' +
                          'SamAccountName,Title,Name,mail')
        else:
            # properties = ' -Properties *'
            properties = (' -Properties xAttrCPR,ObjectGuid,SamAccountName,Title,' +
                          'Name,xBrugertype,EmailAddress, MobilePhone')
        command_end = ' | ConvertTo-Json'

        ps_script = (self._build_user_credential(school) +
                     get_command +
                     search_base +
                     credentials +
                     properties +
                     command_end)

        response = self._run_ps_script(ps_script)

        if not response:
            return_val = []
        else:
            if not isinstance(response, list):
                return_val = [response]
            else:
                return_val = response
        return return_val

    def uncached_read_user(self, user=None, cpr=None):
        logger.debug('Uncached AD read, user {}, cpr {}'.format(user, cpr))
        response = self._get_from_ad(user=user, cpr=cpr, school=True)
        for current_user in response:
            job_title = current_user.get('Title')
            if job_title and job_title.find('FRATR') == 0:
                continue  # These are users that has left

            if 'mail' in current_user:
                current_user['EmailAddress'] = current_user['mail']
                del current_user['mail']

            self.results[current_user['xAttrCPR']] = current_user
            self.results[current_user['SamAccountName']] = current_user

        response = self._get_from_ad(user=user, cpr=cpr, school=False)
        current_user = {}
        for current_user in response:
            job_title = current_user.get('Title')
            if job_title and job_title.find('FRATR') == 0:
                continue  # These are users that has left

            brugertype = current_user.get('xBrugertype')
            if brugertype and brugertype.find('Medarbejder') == -1:
                continue
            if not current_user:
                current_user = {}
            self.results[current_user['xAttrCPR']] = current_user
            self.results[current_user['SamAccountName']] = current_user
        return current_user

    def read_user(self, user=None, cpr=None):
        """
        Read all properties of an AD user. The user can be retrived either by cpr
        or by AD user name.
        :param user: The AD username to retrive.
        :param cpr: cpr number of the user to retrive.
        :return: All properties listed in AD for the user.
        """
        logger.debug('Cached AD read, user {}, cpr {}'.format(user, cpr))
        if (not cpr) and (not user):
            return

        if user:
            dict_key = user
            if user in self.results:
                return self.results[user]

        if cpr:
            dict_key = cpr
            if cpr in self.results:
                return self.results[cpr]

        m = hashlib.sha256()
        m.update(dict_key.encode())
        cache_file = Path('ad_' + m.hexdigest() + '.p')

        if cache_file.is_file():
            with open(str(cache_file), 'rb') as f:
                logger.debug('{} was found in AD cache'.format(dict_key))
                response = pickle.load(f)
                if not response:
                    response = {}
                self.results[dict_key] = response
        else:
            logger.debug('{} was not found in AD cache'.format(dict_key))
            response = self.uncached_read_user(user=user, cpr=cpr)
            with open(str(cache_file), 'wb') as f:
                pickle.dump(response, f, pickle.HIGHEST_PROTOCOL)

        logger.debug('Returned info for {}'.format(dict_key))
        logger.debug(self.results.get(dict_key, {}))
        return self.results.get(dict_key, {})


if __name__ == '__main__':
    import time
    t = time.time()
    ad_reader = ADParameterReader()
    # print(ad_reader.read_encoding())
    user = ad_reader.read_user(user='konroje')
    print(user)
