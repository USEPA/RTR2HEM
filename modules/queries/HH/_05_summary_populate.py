from modules.utils import Join

"""
sheets:
    working_MP07HH_T1Summary
"""


class SummaryPopulate:
    def __init__(self, HH):
        self.HH = HH
        self.qry_07cHH_PopulateSummary()

    # working_MP07HH_T1Summary
    def qry_07cHH_PopulateSummary(self):
        self.HH.working_MP07HH_T1Summary = Join().join(
            [self.HH.working_MP07HH_T1Summary, self.HH.working_MP07bHH_GatherSummary],
            on="PB-HAP Grp",
            how="left",
        )
        self.HH.working_MP07HH_T1Summary = self.HH.working_MP07HH_T1Summary.fillna(0)

        column_order = [
            "Src Cat",
            "Num Facil in Src Cat",
            "Num Facil Emitting Any Assessed PB-HAP",
            "PB-HAP Grp",
            "Num Facil Emitting This PB-HAP",
            "Tier 1 Scrn Thresh (TPY)",
            "date threshold created",
            "(1)Max SV",
            "(2)Facil-Tot Emis*REF (TPY; facil represented by (1))",
            "(3)Facil-Total Emis (TPY; facil represented by (1))",
            "Max Facility",
            "Num Facil Exceeding",
            "Num Facil Exceeding by x10",
            "Num Facil Exceeding by x100",
        ]
        self.HH.working_MP07HH_T1Summary = self.HH.working_MP07HH_T1Summary[
            column_order
        ]
