from modules.queries.QA._01_SourceCatRecs import SourceCatRecs
from modules.queries.QA._02_UniqueFacilities import UniqueFacilities
from modules.queries.QA._03_UniqueSources import UniqueSources
from modules.queries.QA._04_Hemispheres import Hemispheres


def run_qa():
    return [
        SourceCatRecs().run(),
        UniqueFacilities().run(),
        UniqueSources().run(),
        Hemispheres().run(),
    ]
