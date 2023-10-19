from modules.queries.shared_queries import qry_02a_ListPBHAPEmittingFacilities01
from modules.utils import Join, get_static, calc_agg

"""
sheets:
    working_MP07eco_T1Summary
    working_MP07eEco_GatherSummary
"""


class SummaryGather:
    def __init__(self, eco):
        self.eco = eco
        self.qry_07eEco_GatherSummary()

    def qry_02eEco_ListPBHAPEmittingFacilities01(self):
        pbhap_facil = qry_02a_ListPBHAPEmittingFacilities01(self.eco)
        on_column = "shortpb-hap/ecohapname"
        chem_to_update = "Methyl Mercury (Hg2)"

        pbhap_facil.loc[pbhap_facil[on_column] == chem_to_update, on_column] = "Mercury"
        pbhap_facil = pbhap_facil.rename(columns={"ICFFacilityID": "Facility ID"})
        return pbhap_facil

    def qry_02fEco_ListPBHAPEmittingFacilities02(self):
        group_by = ["Facility ID", "sppd_facility_identifier", "ecohap"]
        list_of_ecohaps = get_static("static_MP_ListOfEcoHAPs")
        pbhap_facil = self.qry_02eEco_ListPBHAPEmittingFacilities01()

        pbhap_facil = Join().join(
            [pbhap_facil, list_of_ecohaps],
            left_on="shortpb-hap/ecohapname",
            right_on="ecohap_groupmercury",
        )
        pbhap_facil = pbhap_facil[group_by]
        return pbhap_facil

    def qry_02gEco_CountPBHAPEmittingFacilities_ByPBHAP(self):
        group_by = ["ecohap"]
        pbhap_facilities = self.qry_02fEco_ListPBHAPEmittingFacilities02()

        num_pbhap_facilities = calc_agg(
            pbhap_facilities,
            group_by,
            "count",
            "Facility ID",
            "Number of EcoHAP-Emitting Facilities",
        )

        num_pbhap_facilities = num_pbhap_facilities.rename(
            columns={"ecohap": "EcoHAP Grp"}
        )
        return num_pbhap_facilities

    def qry_06iEco_GetMaxSV(self):
        group_by = [
            "EcoHAP Grp",
            "assessment endpoint",
            "benchmark effects level",
            "benchmark value",
        ]
        max_sv = calc_agg(
            self.eco.working_MP05Eco_T1GrpResults,
            group_by,
            "max",
            "SV (grp)",
            "Max SV (grp)",
        )
        return max_sv

    def qry_06jEco_EmissOfMaxSV(self):
        group_by = [
            "EcoHAP Grp",
            "assessment endpoint",
            "benchmark effects level",
            "benchmark value",
            "Emiss (TPY; grp)",
            "Emiss*EcoEEF (TPY; grp)",
            "SV (grp)",
        ]
        max_sv = self.qry_06iEco_GetMaxSV()
        res = Join().join(
            [self.eco.working_MP05Eco_T1GrpResults, max_sv],
            how="inner",
            left_on=[
                "benchmark effects level",
                "SV (grp)",
                "assessment endpoint",
                "EcoHAP Grp",
            ],
            right_on=[
                "benchmark effects level",
                "Max SV (grp)",
                "assessment endpoint",
                "EcoHAP Grp",
            ],
        )

        res = res.sort_values("Facility ID")
        res = res[group_by + ["Facility ID"]].drop_duplicates(group_by)
        res = res.rename(
            columns={
                "Emiss*EcoEEF (TPY; grp)": "Max Emiss*EcoEEF (TPY; grp)",
                "SV (grp)": "Max SV (grp)",
                "Facility ID": "Facil ID",
            }
        )
        return res

    def qry_06lEco_CountFailingFacilities_PerPBHAP(self):
        def qry_06kEco_ListFailingFacilities_PerPBHAP():
            group_by = [
                "EcoHAP Grp",
                "assessment endpoint",
                "benchmark effects level",
                "benchmark value",
                "Facility ID",
                "SV (grp)",
                "Exceedance?",
            ]
            res = self.eco.working_MP05Eco_T1GrpResults[group_by]
            res = res.loc[res["Exceedance?"] == "Yes"]
            return res

        group_by = [
            "EcoHAP Grp",
            "assessment endpoint",
            "benchmark effects level",
            "benchmark value",
        ]
        exceed = qry_06kEco_ListFailingFacilities_PerPBHAP()
        res = calc_agg(exceed, group_by, "count", "Facility ID", "Num Facil Exceeding")
        return res

    def qry_06nEco_CountFailingFacilitiesx10_PerPBHAP(self):
        def qry_06mEco_ListFailingFacilitiesx10_PerPBHAP():
            group_by = [
                "EcoHAP Grp",
                "assessment endpoint",
                "benchmark effects level",
                "benchmark value",
                "Facility ID",
                "SV (grp)",
                "Exceedance by x10?",
            ]
            res = self.eco.working_MP05Eco_T1GrpResults[group_by]
            res = res.loc[res["Exceedance by x10?"] == "Yes"]
            return res

        group_by = [
            "EcoHAP Grp",
            "assessment endpoint",
            "benchmark effects level",
            "benchmark value",
        ]
        exceed = qry_06mEco_ListFailingFacilitiesx10_PerPBHAP()
        res = calc_agg(
            exceed, group_by, "count", "Facility ID", "Num Facil Exceeding by x10"
        )
        return res

    # working_MP07eco_T1Summary, working_MP07eEco_GatherSummary
    def qry_07eEco_GatherSummary(self):
        num_pbhap_facil = self.qry_02gEco_CountPBHAPEmittingFacilities_ByPBHAP()
        max_sv_emiss = self.qry_06jEco_EmissOfMaxSV()
        count_failing_facil = self.qry_06lEco_CountFailingFacilities_PerPBHAP()
        count_failing_facil_10x = self.qry_06nEco_CountFailingFacilitiesx10_PerPBHAP()

        tmp = Join().join(
            [self.eco.working_MP07Eco_T1Summary, num_pbhap_facil],
            drop_dupe="left",
            how="inner",
            on="EcoHAP Grp",
        )
        tmp = Join().join(
            [
                tmp,
                count_failing_facil,
                count_failing_facil_10x,
                max_sv_emiss,
            ],
            drop_dupe="left",
            how="left",
            on=["assessment endpoint", "EcoHAP Grp", "benchmark effects level"],
        )

        group_by = {
            "Src Cat": "Src Cat",
            "EcoHAP Grp": "EcoHAP Grp",
            "assessment endpoint": "assessment endpoint",
            "Max SV (grp)": "(1)Max SV",
            "Max Emiss*EcoEEF (TPY; grp)": "(2)Facil-Tot Emis*EcoEF (TPY; facil represented by (1))",
            "Emiss (TPY; grp)": "(3)Facil-Total Emis (TPY; facil represented by (1))",
            "benchmark effects level": "benchmark effects level",
            "benchmark value": "benchmark value",
            "Facil ID": "Facil ID",
            "Number of EcoHAP-Emitting Facilities": "Num Facil Emitting This PB-HAP",
            "Num Facil Exceeding": "Num Facil Exceeding",
            "Num Facil Exceeding by x10": "Num Facil Exceeding by x10",
        }
        tmp = tmp[list(group_by.keys())].fillna(0)
        tmp = tmp.rename(columns=group_by)

        self.eco.working_MP07eEco_GatherSummary = tmp
