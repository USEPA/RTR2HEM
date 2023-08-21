from modules.mp_queries.shared_queries import qryMP01b_CountSrcCatFacilities
from modules.utils import Join, calc_agg, set_column

"""
sheets:
    working_MP05Eco_T1GrpResults
"""


class GrpResults:
    column_order = [
        "Src Cat",
        "Num Facil in Src Cat",
        "Facility ID",
        "EcoHAP Grp",
        "Emiss (TPY; grp)",
        "assessment endpoint",
        "Emiss*EcoEEF (TPY; grp)",
        "benchmark effects level",
        "benchmark value",
        "Scrn Thresh (TPY; grp)",
        "Date Scrn Thresh Created",
        "SV (grp)",
        "Exceedance?",
        "Exceedance by x10?",
        "Exceedance by x100?",
    ]

    def __init__(self, eco):
        self.eco = eco
        self.qryMP05bEco_T1GrpResults()

    # working_MP05Eco_T1GrpResults
    def qryMP05bEco_T1GrpResults(self):
        group_by = [
            "Src Cat",
            "Num Facil in Src Cat",
            "Facility ID",
            "EcoHAP Grp",
            "assessment endpoint",
            "benchmark effects level",
            "benchmark value",
            "Scrn Thresh (TPY; grp)",
            "Date Scrn Thresh Created",
        ]

        num_src_cat_facilities = qryMP01b_CountSrcCatFacilities(self.eco)

        tmp = self.eco.working_MP04Eco_T1ChemResults.copy()
        tmp["Num Facil in Src Cat"] = num_src_cat_facilities

        emiss_grp = calc_agg(
            tmp, group_by, "sum", "Emiss (TPY; chem)", "Emiss (TPY; grp)"
        )
        emiss_eef_grp = calc_agg(
            tmp, group_by, "sum", "Emiss*EcoEEF (TPY; chem)", "Emiss*EcoEEF (TPY; grp)"
        )
        sv_grp = calc_agg(tmp, group_by, "sum", "SV (chem)", "SV (grp)")

        tmp = tmp[group_by].drop_duplicates()
        tmp = Join().join(
            [tmp, emiss_grp, emiss_eef_grp, sv_grp], on=group_by, how="left"
        )
        tmp = tmp.sort_values(group_by)

        set_column(tmp, "Exceedance?", self.exceed)
        set_column(tmp, "Exceedance by x10?", self.exceed_10)
        set_column(tmp, "Exceedance by x100?", self.exceed_100)

        self.eco.working_MP05Eco_T1GrpResults = tmp[self.column_order]

    def exceed(self, row):
        try:
            if row["SV (grp)"] < 1.5:
                return "Screens Out"
            return "Yes"
        except:
            return "ERROR"

    def exceed_10(self, row):
        try:
            if row["SV (grp)"] < 1.5:
                return "Screens Out"
            elif row["SV (grp)"] < 10:
                return "No"
            return "Yes"
        except:
            return "ERROR"

    def exceed_100(self, row):
        try:
            if row["SV (grp)"] < 1.5:
                return "Screens Out"
            elif row["SV (grp)"] < 100:
                return "No"
            return "Yes"
        except:
            return "ERROR"
