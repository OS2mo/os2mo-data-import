from unittest import TestCase
from datetime import datetime
from pathlib import Path
from integrations.opus.opus_diff_import import OpusDiffImport
from unittest.mock import MagicMock
import xmltodict
from collections import OrderedDict


class OpusDiffImportTest(OpusDiffImport):
    def __init__(self, *args, **kwargs):
        self.morahelper_mock = MagicMock()
        self.morahelper_mock.read_organisation.return_value = "org_uuid"
        self.MOPrimaryEngagementUpdater_mock = MagicMock()

        super().__init__(*args, **kwargs)

    def _get_mora_helper(self, hostname, use_cache):
        return self.morahelper_mock
    def _primary_updater(self):
        return self.MOPrimaryEngagementUpdater_mock
    def _read_settings(self):
        return {"mora.base": "dummy",
        "mox.base": "dummy"}

class Opus_diff_import_tester(TestCase):
    def setUp(self):
        self.diff = OpusDiffImportTest(datetime.today(), ad_reader=None)

    def test_parser(self):
        self.units, self.employees = self.diff.parser(Path.cwd()/ "integrations/opus/tests/ZLPETESTER_delta.xml", [])
        self.assertIsInstance(self.units, list)
        self.assertIsInstance(self.employees, list)
        self.assertIsInstance(self.units[0], OrderedDict)
        self.assertIsInstance(self.employees[0], OrderedDict)


    def test_diff(self):
        diff.start_re_import(Path.cwd()/ "integrations/opus/tests/ZLPETESTER_delta.xml",include_terminations=True)
       
