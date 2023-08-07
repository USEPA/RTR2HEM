from modules.mp_queries.HH._01_template import Template
from modules.mp_queries.HH._02_group_results import GrpResults
from modules.mp_queries.HH._03_summary_setup import SummarySetup
from modules.mp_queries.HH._04_summary_gather import SummaryGather
from modules.mp_queries.HH._05_summary_populate import SummaryPopulate


def run_HH_module(working_crosswalk, latlons, accdb):
    HH_obj = Template(working_crosswalk, latlons)
    GrpResults(HH_obj)
    SummarySetup(HH_obj)
    SummaryGather(HH_obj)
    SummaryPopulate(HH_obj)

    accdb.write(
        "05 - T1 HumHealth Mpath Scrn By Facil-Chem",
        HH_obj.working_MP04HH_T1ChemResults,
    )
    accdb.write(
        "06 - T1 HumHealth Mpath Scrn By Facil-PBHAPGrp",
        HH_obj.working_MP05HH_T1GrpResults,
    )
    accdb.write("07 - T1 HumHealth Mpath Scrn Summary", HH_obj.working_MP07HH_T1Summary)
    return HH_obj
