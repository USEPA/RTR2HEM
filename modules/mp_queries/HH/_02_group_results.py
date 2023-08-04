from modules.utils import calc_agg, join, set_column

"""
sheets:
    working_MP05HH_T1GrpResults
"""


class GrpResults:
    def __init__(self, HH):
        self.HH = HH
        self.qryMP05aHH_T1GrpResults()

    def qryMP01a_ListSrcCatFacilities(self):
        group_by = ["ICFFacilityID", "sppd_facility_identifier", "ICFCatLevelModeling"]
        tmp = self.HH.working_crosswalk
        tmp = tmp.loc[tmp["ICFCatLevelModeling"] == "Yes"]

        tmp = tmp.sort_values(group_by)
        tmp = tmp[group_by].drop("ICFCatLevelModeling", axis=1)
        tmp = tmp.drop_duplicates()
        return tmp

    def qryMP01b_CountSrcCatFacilities(self):
        """
        SELECT Count(qryMP01a_ListSrcCatFacilities.[Facility ID]) AS [Num Facil in Src Cat]
        FROM qryMP01a_ListSrcCatFacilities;
        """
        src_cat_facilities = self.qryMP01a_ListSrcCatFacilities()
        self.HH.num_src_cat_facilities = len(src_cat_facilities.index)
        return self.HH.num_src_cat_facilities

    # working_MP05HH_T1GrpResults
    def qryMP05aHH_T1GrpResults(self):
        # working_MP04HH_T1ChemResults
        # qryMP01b_CountSrcCatFacilities
        group_by = [
            "Src Cat",
            "Num Facil in Src Cat",
            "Facility ID",
            "PB-HAP Grp",
            "Scrn Thresh (TPY; grp)",
            "Date Scrn Thresh Created",
        ]

        num_src_cat_facilities = self.qryMP01b_CountSrcCatFacilities()

        tmp = self.HH.working_MP04HH_T1ChemResults
        tmp["Num Facil in Src Cat"] = num_src_cat_facilities

        emiss_grp = calc_agg(
            tmp, group_by, "sum", "Emiss (TPY; chem)", "Emiss (TPY; grp)"
        )
        emiss_ref_grp = calc_agg(
            tmp, group_by, "sum", "Emiss*REF (TPY; chem)", "Emiss*REF (TPY; grp)"
        )
        sv_grp = calc_agg(tmp, group_by, "sum", "SV (chem)", "SV (grp)")

        tmp = tmp[group_by].drop_duplicates()
        tmp = join([tmp, emiss_grp, emiss_ref_grp, sv_grp], on=group_by)
        tmp = tmp.sort_values(group_by)

        set_column(tmp, "Exceedance?", self.exceed)
        set_column(tmp, "Exceedance by x10?", self.exceed_10)
        set_column(tmp, "Exceedance by x100?", self.exceed_100)

        self.HH.working_MP05HH_T1GrpResults = tmp

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
