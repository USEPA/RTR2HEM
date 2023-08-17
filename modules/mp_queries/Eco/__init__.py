from modules.mp_queries.Eco._01_template import Template
from modules.mp_queries.Eco._02_group_results import GrpResults
from modules.mp_queries.Eco._03_summary_setup import SummarySetup
from modules.mp_queries.Eco._04_summary_gather import SummaryGather


def run_Eco_module(working_crosswalk, working_eco_crosswalk, latlons):
    Eco_obj = Template(working_crosswalk, working_eco_crosswalk, latlons)
    GrpResults(Eco_obj)
    SummarySetup(Eco_obj)
    SummaryGather(Eco_obj)
    return Eco_obj
