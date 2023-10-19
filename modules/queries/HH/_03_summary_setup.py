from modules.queries.shared_queries import (
    qry_01b_CountSrcCatFacilities,
    qry_02c_CountPBHAPEmittingFacilities,
)
from modules.utils import get_static

"""
sheets:
    working_MP07HH_T1Summary
"""


class SummarySetup:
    working_MP07HH_T1Summary = None

    def __init__(self, HH):
        self.HH = HH
        self.qry_07aHH_PrepareShellOfSummary()

    # working_MP07HH_T1Summary
    def qry_07aHH_PrepareShellOfSummary(self):
        screen_thresholds = get_static("static_MP_HHScreeningThresholds")

        screen_thresholds["Num Facil in Src Cat"] = qry_01b_CountSrcCatFacilities(
            self.HH
        )

        screen_thresholds[
            "Num Facil Emitting Any Assessed PB-HAP"
        ] = qry_02c_CountPBHAPEmittingFacilities(self.HH)

        screen_thresholds["Src Cat"] = ""
        screen_thresholds = screen_thresholds.sort_values("shortpb-hapname")

        screen_thresholds = screen_thresholds.rename(
            columns={
                "shortpb-hapname": "PB-HAP Grp",
                "tier 1 screening threshold (tpy)": "Tier 1 Scrn Thresh (TPY)",
            }
        )

        self.HH.working_MP07HH_T1Summary = screen_thresholds
