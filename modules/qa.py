from modules.queries.QA._01_SourceCatRecs import SourceCatRecs
from modules.queries.QA._02_UniqueFacilities import UniqueFacilities
from modules.utils import config

"""
will need to add a button as an additional step in GUI
"""


class QA:
    results = {}

    def __init__(self):
        pass

    def run(self):
        self.results["SourceCatRecs"] = SourceCatRecs().run()
        self.results["UniqueFacilities"] = UniqueFacilities().run()
