from modules.mp_queries.shared_queries import (
    qryMP01b_CountSrcCatFacilities,
    qryMP02c_CountPBHAPEmittingFacilities,
)
from modules.utils import Join, get_static, calc_agg

"""
sheets:
    working_MP07Eco_T1Summary
"""


class SummarySetup:
    working_MP07Eco_T1Summary = None

    def __init__(self, eco):
        self.eco = eco
        self.qryMP07dEco_PrepareShellOfSummary()

    # working_MP07Eco_T1Summary
    def qryMP07dEco_PrepareShellOfSummary(self):
        screen_thresholds = get_static("static_MP_EcoScreeningThresholds")

        screen_thresholds[
            "Num Facil Emitting Any HAP"
        ] = qryMP01b_CountSrcCatFacilities(self.eco)

        screen_thresholds[
            "Num Facil Emitting Any Assessed EcoHAP"
        ] = qryMP02c_CountPBHAPEmittingFacilities(self.eco)

        screen_thresholds["Src Cat"] = ""
        screen_thresholds = screen_thresholds.sort_values("shortpb-hap/ecohapname")

        screen_thresholds = screen_thresholds.rename(
            columns={
                "shortpb-hap/ecohapname": "EcoHAP Grp",
                "tier 1 eco screening threshold (tpy)": "Tier 1 Scrn Thresh (TPY)",
            }
        )

        self.eco.working_MP07Eco_T1Summary = screen_thresholds
