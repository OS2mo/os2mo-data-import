import logging

# import ad_logger
# import ad_exceptions

from pathlib import Path

from ad_writer import ADWriter

logger = logging.getLogger("AdExecute")


EXECUTION_REPLACEMENT_SCAFFOLD = {
    '%OS2MO_AD_BRUGERNAVN%': None,
    '%OS2MO_BRUGER_FORNAVN%': None,
    '%OS2MO_BRUGER_EFTERNAVN%':  None,
    '%OS2MO_BRUGER_CPR%':  None,
    '%OS2MO_LEDER_EMAIL%': None,
    '%OS2MO_LEDER_NAVN%': None,
    '%OS2MO_BRUGER_ENHED%': None,
    '%OS2MO_BRUGER_ENHED_UUID%': None
}


# Dette ender forentlig med at være indlejret i AD writer, men koden for nu for
# sig selv for at undgå potentielle mergekonflikter medn AD writer stadig er i
# review.
class ADExecute(ADWriter):
    def __init__(self):
        super().__init__()
        self.script = None

    def _validate_script(self):
        if self.script is None:
            msg = 'No script loaded!'
            logger.error(msg)
            # TODO: Should we make an explicit exception for this?
            raise Exception(msg)

        lines = self.script.split('\n')

        keywords = set()
        for line in lines:
            if line.find('#') > -1:
                line = line[0:line.find('#')]
            search_index = 0
            index = line.find('%OS2MO_', search_index)
            while index > 0:
                end_index = line.find('%', index + 1)
                keywords.add(line[index:end_index + 1])
                search_index = end_index
                index = line.find('%OS2MO_', search_index)

        keyword_errors = set()
        for keyword in keywords:
            if keyword not in EXECUTION_REPLACEMENT_SCAFFOLD:
                keyword_errors.add(keyword)
        if keyword_errors:
            msg = 'Unknown keywords present in template: {}'.format(keyword_errors)
            logger.error(msg)
            # TODO: Should we make an explicit exception for this?
            raise Exception(msg)

    def _remove_block_comments(self):
        search_index = 0
        index = self.script.find('<#', search_index)
        remove_ranges = []
        while index > 0:
            end_index = self.script.find('#>', index + 1) + 3
            remove_ranges.append((index, end_index))
            search_index = end_index
            index = self.script.find('<%', search_index)

        for remove_range in remove_ranges:
            self.script = (self.script[:remove_range[0]] +
                           self.script[remove_range[1]:])

    def fill_script_template(self, mo_user_uuid):
        mo_info = self.read_ad_informaion_from_mo(mo_user_uuid, read_manager=True)
        ad_user = self.get_from_ad(cpr=mo_info['cpr'])
        user_sam = ad_user[0]['SamAccountName']

        execution_replacement = EXECUTION_REPLACEMENT_SCAFFOLD.copy()
        execution_replacement['%OS2MO_AD_BRUGERNAVN%'] = user_sam
        execution_replacement['%OS2MO_BRUGER_FORNAVN%'] = mo_info['name'][0]
        execution_replacement['%OS2MO_BRUGER_EFTERNAVN%'] = mo_info['name'][1]
        execution_replacement['%OS2MO_BRUGER_CPR%'] = mo_info['cpr']
        execution_replacement['%OS2MO_LEDER_EMAIL%'] = mo_info['manager_mail']
        execution_replacement['%OS2MO_LEDER_NAVN%'] = mo_info['manager_name']
        execution_replacement['%OS2MO_BRUGER_ENHED%'] = mo_info['unit']
        execution_replacement['%OS2MO_BRUGER_ENHED_UUID%'] = mo_info['unit_uuid']
        if None in execution_replacement:
            msg = 'Not all replacement values available'
            logger.error(msg)
            # TODO: Should we make an explicit exception for this?
            raise Exception(msg)

        actual_script = ''
        lines = self.script.split('\n')
        for line in lines:
            if line.find('#') > -1:
                actual_line = line[0:line.find('#')]
            else:
                actual_line = line

            for key, replacement in execution_replacement.items():
                actual_line = actual_line.replace(key, replacement)
            if actual_line.strip():
                actual_script += actual_line + '\n'

        # self.script = self.script.replace(key, replacement)
        return True

    def read_script_template(self, script_name):
        p = Path('scripts/{}'.format(script_name))
        self.script = p.read_text()

        self._validate_script()


if __name__ == '__main__':
    exe = ADExecute()

    script_name = 'send_email.ps_template'
    mo_user_uuid = ''
    exe.read_script_template(script_name)

    exe._remove_block_comments()

    # exe.fill_script_template(mo_user_uuid)
    # print(exe.script)
