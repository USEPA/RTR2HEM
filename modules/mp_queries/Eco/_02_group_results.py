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
        "Assessment Endpoint",
        "Emiss*EcoEEF (TPY; grp)",
        "Benchmark Effects Level",
        "Benchmark Value",
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

    def qryMP01a_ListSrcCatFacilities(self):
        group_by = ["ICFFacilityID", "sppd_facility_identifier", "ICFCatLevelModeling"]
        tmp = self.eco.working_crosswalk
        tmp = tmp.loc[tmp["ICFCatLevelModeling"] == "Yes"]

        tmp = tmp.sort_values(group_by)
        tmp = tmp[group_by].drop("ICFCatLevelModeling", axis=1)
        tmp = tmp.drop_duplicates()
        return tmp

    # NOTE - this query is re-used in both HH and eco
    def qryMP01b_CountSrcCatFacilities(self):
        src_cat_facilities = self.qryMP01a_ListSrcCatFacilities()
        self.eco.num_src_cat_facilities = len(src_cat_facilities.index)
        return self.eco.num_src_cat_facilities

    # working_MP05Eco_T1GrpResults
    def qryMP05bEco_T1GrpResults(self):
        """
        SELECT working_MP04Eco_T1ChemResults.[Src Cat], 
        qryMP01b_CountSrcCatFacilities.[Num Facil in Src Cat], 
        working_MP04Eco_T1ChemResults.[Facility ID], 
        working_MP04Eco_T1ChemResults.[EcoHAP Grp], 
        Sum(working_MP04Eco_T1ChemResults.[Emiss (TPY; chem)]) AS [Emiss (TPY; grp)], 
        working_MP04Eco_T1ChemResults.[Assessment Endpoint], 
        Sum(working_MP04Eco_T1ChemResults.[Emiss*EcoEEF (TPY; chem)]) AS [Emiss*EcoEEF (TPY; grp)], 
        working_MP04Eco_T1ChemResults.[Benchmark Effects Level], 
        working_MP04Eco_T1ChemResults.[Benchmark Value], 
        working_MP04Eco_T1ChemResults.[Scrn Thresh (TPY; grp)], 
        working_MP04Eco_T1ChemResults.[Date Scrn Thresh Created], 
        Sum(working_MP04Eco_T1ChemResults.[SV (chem)]) AS [SV (grp)], 
        IIf(Sum([SV (chem)])<1.5,"Screens Out",IIf(Sum([SV (chem)])>=1.5,"Yes","ERROR")) AS [Exceedance?], 
        IIf(Sum([SV (chem)])<1.5,"Screens Out",IIf(Sum([SV (chem)])<10,"No",IIf(Sum([SV (chem)])>=10,"Yes","ERROR"))) AS [Exceedance by x10?], 
        IIf(Sum([SV (chem)])<1.5,"Screens Out",IIf(Sum([SV (chem)])<100,"No",IIf(Sum([SV (chem)])>=100,"Yes","ERROR"))) AS [Exceedance by x100?] 
        INTO working_MP05Eco_T1GrpResults

        FROM working_MP04Eco_T1ChemResults, qryMP01b_CountSrcCatFacilities

        GROUP BY working_MP04Eco_T1ChemResults.[Src Cat], 
        qryMP01b_CountSrcCatFacilities.[Num Facil in Src Cat], 
        working_MP04Eco_T1ChemResults.[Facility ID], 
        working_MP04Eco_T1ChemResults.[EcoHAP Grp], 
        working_MP04Eco_T1ChemResults.[Assessment Endpoint], 
        working_MP04Eco_T1ChemResults.[Benchmark Effects Level], 
        working_MP04Eco_T1ChemResults.[Benchmark Value], 
        working_MP04Eco_T1ChemResults.[Scrn Thresh (TPY; grp)], 
        working_MP04Eco_T1ChemResults.[Date Scrn Thresh Created]

        ORDER BY working_MP04Eco_T1ChemResults.[Src Cat], 
        working_MP04Eco_T1ChemResults.[Facility ID], 
        working_MP04Eco_T1ChemResults.[EcoHAP Grp];
        """
        group_by = [
            "Src Cat",
            "Num Facil in Src Cat",
            "Facility ID",
            "EcoHAP Grp",
            "Assessment Endpoint",
            "Benchmark Effects Level",
            "Benchmark Value",
            "Scrn Thresh (TPY; grp)",
            "Date Scrn Thresh Created",
        ]

        num_src_cat_facilities = self.qryMP01b_CountSrcCatFacilities()

        tmp = self.eco.working_MP04Eco_T1ChemResults.copy()
        tmp["Num Facil in Src Cat"] = num_src_cat_facilities

        emiss_grp = calc_agg(
            tmp, group_by, "sum", "Emiss (TPY; chem)", "Emiss (TPY; grp)"
        )
        emiss_eef_grp = calc_agg(
            tmp, group_by, "sum", "Emiss*EcoEEF (TPY; chem)", "Emiss*EcoEEF (TPY; grp)"
        )
        sv_grp = calc_agg(tmp, group_by, "sum", "SV (chem)", "SV (grp)")

        tmp = tmp[group_by].drop_duplicates(group_by)
        tmp = Join().join([tmp, emiss_grp, emiss_eef_grp, sv_grp], on=group_by, how='left')
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
