import json
import logging
import pathlib

from reports.query_actualstate import *

LOG_LEVEL = logging.DEBUG
LOG_FILE = "Frederikshavn_reports.log"

logger = logging.getLogger("Frederikshavn_reports")

logging.basicConfig(
    format="%(levelname)s %(asctime)s %(name)s %(message)s",
    level=LOG_LEVEL,
    filename=LOG_FILE,
)

if __name__ == "__main__":
    # Læs fra settings
    settings = json.loads((pathlib.Path(".") / "settings/settings.json").read_text())
    query_path = settings["mora.folder.query_export"]
    logger.debug("Running reports for Frederikshavn")
    run_report(
        list_MED_members,
        "MED",
        "MED-organisationen",
        query_path + "/MED_medlemmer.xlsx",
    )
    logger.debug("MED report done.")
    run_report(
        list_employees,
        "Ansatte",
        "Frederikshavn Kommune",
        query_path + "/Ansatte.xlsx",
    )
    logger.debug("Employee report done.")

    logger.debug("All reports for Frederikshavn done")
