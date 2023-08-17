from modules.mp_queries.shared_queries import (
    qryMP01b_CountSrcCatFacilities,
    qryMP02c_CountPBHAPEmittingFacilities,
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
        self.qryMP07aHH_PrepareShellOfSummary()

    # working_MP07HH_T1Summary
    def qryMP07aHH_PrepareShellOfSummary(self):
        screen_thresholds = get_static("static_MP_HHScreeningThresholds")

        screen_thresholds["Num Facil in Src Cat"] = qryMP01b_CountSrcCatFacilities(
            self.HH
        )

        screen_thresholds[
            "Num Facil Emitting Any Assessed PB-HAP"
        ] = qryMP02c_CountPBHAPEmittingFacilities(self.HH)

        screen_thresholds["Src Cat"] = ""
        screen_thresholds = screen_thresholds.sort_values("shortpb-hapname")

        screen_thresholds = screen_thresholds.rename(
            columns={
                "shortpb-hapname": "PB-HAP Grp",
                "tier 1 screening threshold (tpy)": "Tier 1 Scrn Thresh (TPY)",
            }
        )

        self.HH.working_MP07HH_T1Summary = screen_thresholds
