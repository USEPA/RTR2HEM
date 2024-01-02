from ._01_template import Template
from ._02_group_results import GrpResults
from ._03_summary_setup import SummarySetup
from ._04_summary_gather import SummaryGather
from ._05_summary_populate import SummaryPopulate

from src.utils import config


def run_HH_module(working_crosswalk, latlons):
    HH_obj = Template(working_crosswalk, latlons)
    GrpResults(HH_obj)
    SummarySetup(HH_obj)
    SummaryGather(HH_obj)
    SummaryPopulate(HH_obj)

    src_cat_str = f"{config.src_cat_name}_{config.emission_type}"
    HH_obj.working_MP04HH_T1ChemResults["Src Cat"] = src_cat_str
    HH_obj.working_MP05HH_T1GrpResults["Src Cat"] = src_cat_str
    HH_obj.working_MP07HH_T1Summary["Src Cat"] = src_cat_str

    config.out.accdb.write(
        "05 - T1 HumHealth Mpath Scrn By Facil-Chem",
        HH_obj.working_MP04HH_T1ChemResults,
    )
    config.out.accdb.write(
        "06 - T1 HumHealth Mpath Scrn By Facil-PBHAPGrp",
        HH_obj.working_MP05HH_T1GrpResults,
    )
    config.out.accdb.write(
        "07 - T1 HumHealth Mpath Scrn Summary", HH_obj.working_MP07HH_T1Summary
    )
    return HH_obj
