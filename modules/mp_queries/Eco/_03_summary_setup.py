from modules.mp_queries.shared_queries import qryMP01b_CountSrcCatFacilities, qryMP02c_CountPBHAPEmittingFacilities
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
        """
        SELECT "" AS [Src Cat],
        qryMP01b_CountSrcCatFacilities.[Num Facil in Src Cat] AS [Num Facil Emitting Any HAP],
        qryMP02c_CountPBHAPEmittingFacilities.[Num Facil Emitting PB-HAPs] AS [Num Facil Emitting Any Assessed EcoHAP],
        static_MP_EcoScreeningThresholds.[ShortPB-HAP/EcoHAPName] AS [EcoHAP Grp],
        CLng(0) AS [Num Facil Emitting This EcoHAP],
        static_MP_EcoScreeningThresholds.[Assessment Endpoint],
        static_MP_EcoScreeningThresholds.[Benchmark Effects Level],
        static_MP_EcoScreeningThresholds.[Benchmark Value],
        static_MP_EcoScreeningThresholds.[Tier 1 Eco Screening Threshold (TPY)] AS [Tier 1 Scrn Thresh (TPY)],
        static_MP_EcoScreeningThresholds.[Date Threshold Created],
        CDbl(0) AS [(1)Max SV], CDbl(0) AS [(2)Facil-Tot Emis*EcoEF (TPY; facil represented by (1))],
        CDbl(0) AS [(3)Facil-Total Emis (TPY; facil represented by (1))],
        "" AS [Max Facility],
        CLng(0) AS [Num Facil Exceeding],
        CLng(0) AS [Num Facil Exceeding by x10]
        INTO working_MP07Eco_T1Summary

        FROM static_MP_EcoScreeningThresholds,
        qryMP01b_CountSrcCatFacilities,
        qryMP02c_CountPBHAPEmittingFacilities

        ORDER BY static_MP_EcoScreeningThresholds.[ShortPB-HAP/EcoHAPName],
        static_MP_EcoScreeningThresholds.[Benchmark Effects Level];
        """

        screen_thresholds = get_static("static_MP_EcoScreeningThresholds")

        screen_thresholds["Num Facil Emitting Any HAP"] = qryMP01b_CountSrcCatFacilities(self.eco)
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
