from modules.mp_queries.HH._01_template import Template
from modules.mp_queries.HH._02_group_results import GrpResults
from modules.mp_queries.HH._03_summary_setup import SummarySetup
from modules.mp_queries.HH._04_summary_gather import SummaryGather
from modules.mp_queries.HH._05_summary_populate import SummaryPopulate


def run_HH_module(working_crosswalk, latlons):
    HH_obj = Template(working_crosswalk, latlons)
    GrpResults(HH_obj)
    SummarySetup(HH_obj)
    SummaryGather(HH_obj)
    SummaryPopulate(HH_obj)
    return HH_obj
