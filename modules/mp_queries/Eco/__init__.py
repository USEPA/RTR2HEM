from modules.mp_queries.Eco._01_template import Template
from modules.mp_queries.Eco._02_group_results import GrpResults
from modules.mp_queries.Eco._03_summary_setup import SummarySetup
from modules.mp_queries.Eco._04_summary_gather import SummaryGather
from modules.mp_queries.Eco._05_summary_populate import SummaryPopulate

from modules.utils import config


def run_Eco_module(working_crosswalk, working_eco_crosswalk, latlons, accdb):
    Eco_obj = Template(working_crosswalk, working_eco_crosswalk, latlons)
    GrpResults(Eco_obj)
    SummarySetup(Eco_obj)
    SummaryGather(Eco_obj)
    SummaryPopulate(Eco_obj)

    src_cat_str = f"{config.src_cat_name}_{config.emission_type}"
    Eco_obj.working_MP04Eco_T1ChemResults["Src Cat"] = src_cat_str
    Eco_obj.working_MP05Eco_T1GrpResults["Src Cat"] = src_cat_str
    Eco_obj.working_MP07Eco_T1Summary["Src Cat"] = src_cat_str

    accdb.write(
        "08 - T1 Eco Mpath Scrn By Facil-Chem",
        Eco_obj.working_MP04Eco_T1ChemResults,
    )
    accdb.write(
        "09 - T1 Eco Mpath Scrn By Facil-PBHAPGrp",
        Eco_obj.working_MP05Eco_T1GrpResults,
    )
    accdb.write("10 - T1 Eco Mpath Scrn Summary", Eco_obj.working_MP07Eco_T1Summary)
    return Eco_obj
