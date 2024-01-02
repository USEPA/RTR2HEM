from src.modules.queries.shared_queries import qry_01b_CountSrcCatFacilities
from src.utils import Join, calc_agg, vset

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
        self.qry_05bEco_T1GrpResults()

    # working_MP05Eco_T1GrpResults
    def qry_05bEco_T1GrpResults(self):
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

        num_src_cat_facilities = qry_01b_CountSrcCatFacilities(self.eco)

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

        vset(tmp, "Exceedance?", self.exceed, ["SV (grp)"])
        vset(tmp, "Exceedance by x10?", self.exceed_10, ["SV (grp)"])
        vset(tmp, "Exceedance by x100?", self.exceed_100, ["SV (grp)"])

        self.eco.working_MP05Eco_T1GrpResults = tmp[self.column_order]

    def exceed(self, sv_grp):
        try:
            if sv_grp < 1.5:
                return "Screens Out"
            return "Yes"
        except:
            return "ERROR"

    def exceed_10(self, sv_grp):
        try:
            if sv_grp < 1.5:
                return "Screens Out"
            elif sv_grp < 10:
                return "No"
            return "Yes"
        except:
            return "ERROR"

    def exceed_100(self, sv_grp):
        try:
            if sv_grp < 1.5:
                return "Screens Out"
            elif sv_grp < 100:
                return "No"
            return "Yes"
        except:
            return "ERROR"
