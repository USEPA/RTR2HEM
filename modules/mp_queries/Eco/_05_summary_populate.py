from modules.utils import Join

"""
sheets:
    working_MP07Eco_T1Summary
"""


class SummaryPopulate:
    def __init__(self, eco):
        self.eco = eco
        self.qry_07fEco_PopulateSummary()

    # working_MP07Eco_T1Summary
    def qry_07fEco_PopulateSummary(self):
        self.eco.working_MP07Eco_T1Summary = Join().join(
            [
                self.eco.working_MP07Eco_T1Summary,
                self.eco.working_MP07eEco_GatherSummary,
            ],
            on=[
                "Src Cat",
                "EcoHAP Grp",
                "assessment endpoint",
                "benchmark effects level",
            ],
            how="left",
        )
        self.eco.working_MP07Eco_T1Summary = self.eco.working_MP07Eco_T1Summary.fillna(
            0
        )

        columns = {
            "Src Cat": "Src Cat",
            "Num Facil Emitting Any HAP": "Num Facil Emitting Any HAP",
            "Num Facil Emitting Any Assessed EcoHAP": "Num Facil Emitting Any Assessed EcoHAP",
            "EcoHAP Grp": "EcoHAP Grp",
            "Num Facil Emitting This PB-HAP": "Num Facil Emitting This EcoHAP",
            "assessment endpoint": "Assessment Endpoint",
            "benchmark effects level": "Benchmark Effects Level",
            "benchmark value": "Benchmark Value",
            "Tier 1 Scrn Thresh (TPY)": "Tier 1 Scrn Thresh (TPY)",
            "date threshold created": "Date Threshold Created",
            "(1)Max SV": "(1)Max SV",
            "(2)Facil-Tot Emis*EcoEF (TPY; facil represented by (1))": "(2)Facil-Tot Emis*EcoEF (TPY; facil represented by (1))",
            "(3)Facil-Total Emis (TPY; facil represented by (1))": "(3)Facil-Total Emis (TPY; facil represented by (1))",
            "Facil ID": "Max Facility",
            "Num Facil Exceeding": "Num Facil Exceeding",
            "Num Facil Exceeding by x10": "Num Facil Exceeding by x10",
        }

        self.eco.working_MP07Eco_T1Summary = self.eco.working_MP07Eco_T1Summary[
            list(columns.keys())
        ]

        self.eco.working_MP07Eco_T1Summary = self.eco.working_MP07Eco_T1Summary.rename(
            columns=columns
        )

        sort_by = [
            "Max Facility",
            "EcoHAP Grp",
            "Assessment Endpoint",
            "Benchmark Effects Level",
        ]
        self.eco.working_MP07Eco_T1Summary = (
            self.eco.working_MP07Eco_T1Summary.sort_values(sort_by)
        )
