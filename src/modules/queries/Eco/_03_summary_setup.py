from src.modules.queries.shared_queries import (
    qry_01b_CountSrcCatFacilities,
    qry_02c_CountPBHAPEmittingFacilities,
)
from src.utils import Join, get_static, calc_agg

"""
sheets:
    working_MP07Eco_T1Summary
"""


class SummarySetup:
    working_MP07Eco_T1Summary = None

    def __init__(self, eco):
        self.eco = eco
        self.qry_07dEco_PrepareShellOfSummary()

    # working_MP07Eco_T1Summary
    def qry_07dEco_PrepareShellOfSummary(self):
        screen_thresholds = get_static("static_MP_EcoScreeningThresholds")

        screen_thresholds["Num Facil Emitting Any HAP"] = qry_01b_CountSrcCatFacilities(
            self.eco
        )

        screen_thresholds[
            "Num Facil Emitting Any Assessed EcoHAP"
        ] = qry_02c_CountPBHAPEmittingFacilities(self.eco)

        screen_thresholds["Src Cat"] = ""
        screen_thresholds = screen_thresholds.sort_values("shortpb-hap/ecohapname")

        screen_thresholds = screen_thresholds.rename(
            columns={
                "shortpb-hap/ecohapname": "EcoHAP Grp",
                "tier 1 eco screening threshold (tpy)": "Tier 1 Scrn Thresh (TPY)",
            }
        )

        self.eco.working_MP07Eco_T1Summary = screen_thresholds
