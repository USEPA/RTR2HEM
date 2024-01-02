from src.modules.queries.shared_queries import qry_02a_ListPBHAPEmittingFacilities01
from src.utils import Join, get_static, calc_agg

"""
sheets:
    working_MP07HH_T1Summary
    working_MP07bHH_GatherSummary
"""


class SummaryGather:
    def __init__(self, HH):
        self.HH = HH
        self.qry_07bHH_GatherSummary()

    def qry_02dHH_CountPBHAPEmittingFacilities_ByPBHAP(self):
        group_by = ["shortpb-hap/ecohapname"]
        pbhap_facilities = qry_02a_ListPBHAPEmittingFacilities01(self.HH)

        num_pbhap_facilities = calc_agg(
            pbhap_facilities,
            group_by,
            "count",
            "ICFFacilityID",
            "Num Facil Emitting This PB-HAP",
        )

        num_pbhap_facilities = num_pbhap_facilities.rename(
            columns={"shortpb-hap/ecohapname": "PB-HAP Grp"}
        )
        return num_pbhap_facilities

    def qry_06aHH_GetMaxSV(self):
        group_by = ["PB-HAP Grp"]
        max_sv = calc_agg(
            self.HH.working_MP05HH_T1GrpResults, group_by, "max", "SV (grp)", "Max SV"
        )
        return max_sv

    def qry_06bHH_EmissOfMaxSV(self):
        group_by = [
            "PB-HAP Grp",
            "Emiss (TPY; grp)",
            "Emiss*REF (TPY; grp)",
            "SV (grp)",
        ]
        max_sv = self.qry_06aHH_GetMaxSV()
        res = Join().join(
            [self.HH.working_MP05HH_T1GrpResults, max_sv],
            how="inner",
            left_on=["PB-HAP Grp", "SV (grp)"],
            right_on=["PB-HAP Grp", "Max SV"],
        )

        res = res.sort_values("Facility ID")
        res = res[group_by + ["Facility ID"]].drop_duplicates(group_by)
        res = res.rename(
            columns={
                "Emiss*REF (TPY; grp)": "Max Emiss*REF (TPY; grp)",
                "SV (grp)": "Max SV (grp)",
                "Facility ID": "Facil ID",
            }
        )
        return res

    def qry_06dHH_CountFailingFacilities_PerPBHAP(self):
        def qry_06cHH_ListFailingFacilities_PerPBHAP():
            group_by = ["PB-HAP Grp", "Facility ID", "SV (grp)", "Exceedance?"]
            res = self.HH.working_MP05HH_T1GrpResults[group_by]
            res = res.loc[res["Exceedance?"] == "Yes"]
            return res

        group_by = ["PB-HAP Grp"]
        exceed = qry_06cHH_ListFailingFacilities_PerPBHAP()
        res = calc_agg(exceed, group_by, "count", "Facility ID", "Num Facil Exceeding")
        return res

    def qry_06fHH_CountFailingFacilitiesx10_PerPBHAP(self):
        def qry_06eHH_ListFailingFacilitiesx10_PerPBHAP():
            group_by = ["PB-HAP Grp", "Facility ID", "SV (grp)", "Exceedance by x10?"]
            res = self.HH.working_MP05HH_T1GrpResults[group_by]
            res = res.loc[res["Exceedance by x10?"] == "Yes"]
            return res

        group_by = ["PB-HAP Grp"]
        exceed = qry_06eHH_ListFailingFacilitiesx10_PerPBHAP()
        res = calc_agg(
            exceed, group_by, "count", "Facility ID", "Num Facil Exceeding by x10"
        )
        return res

    def qry_06hHH_CountFailingFacilitiesx100_PerPBHAP(self):
        def qry_06gHH_ListFailingFacilitiesx100_PerPBHAP():
            group_by = ["PB-HAP Grp", "Facility ID", "SV (grp)", "Exceedance by x100?"]
            res = self.HH.working_MP05HH_T1GrpResults[group_by]
            res = res.loc[res["Exceedance by x100?"] == "Yes"]
            return res

        group_by = ["PB-HAP Grp"]
        exceed = qry_06gHH_ListFailingFacilitiesx100_PerPBHAP()
        res = calc_agg(
            exceed, group_by, "count", "Facility ID", "Num Facil Exceeding by x100"
        )
        return res

    # working_MP07HH_T1Summary, working_MP07bHH_GatherSummary
    def qry_07bHH_GatherSummary(self):
        num_pbhap_facil = self.qry_02dHH_CountPBHAPEmittingFacilities_ByPBHAP()
        max_sv_emiss = self.qry_06bHH_EmissOfMaxSV()
        count_failing_facil = self.qry_06dHH_CountFailingFacilities_PerPBHAP()
        count_failing_facil_10x = self.qry_06fHH_CountFailingFacilitiesx10_PerPBHAP()
        count_failing_facil_100x = self.qry_06hHH_CountFailingFacilitiesx100_PerPBHAP()

        tmp = Join().join(
            [self.HH.working_MP07HH_T1Summary, num_pbhap_facil],
            drop_dupe="left",
            how="inner",
            on="PB-HAP Grp",
        )
        tmp = Join().join(
            [
                tmp,
                count_failing_facil,
                count_failing_facil_10x,
                count_failing_facil_100x,
                max_sv_emiss,
            ],
            drop_dupe="left",
            how="left",
            on="PB-HAP Grp",
        )

        tmp["(3)Facil-Total Emis (TPY; facil represented by (1))"] = tmp[
            "Max Emiss*REF (TPY; grp)"
        ]

        group_by = {
            "Src Cat": "Src Cat",
            "PB-HAP Grp": "PB-HAP Grp",
            "Max SV (grp)": "(1)Max SV",
            "Max Emiss*REF (TPY; grp)": "(2)Facil-Tot Emis*REF (TPY; facil represented by (1))",
            "(3)Facil-Total Emis (TPY; facil represented by (1))": "(3)Facil-Total Emis (TPY; facil represented by (1))",
            "Facil ID": "Max Facility",
            "Num Facil Emitting This PB-HAP": "Num Facil Emitting This PB-HAP",
            "Num Facil Exceeding": "Num Facil Exceeding",
            "Num Facil Exceeding by x10": "Num Facil Exceeding by x10",
            "Num Facil Exceeding by x100": "Num Facil Exceeding by x100",
        }
        tmp = tmp[list(group_by.keys())].fillna(0)
        tmp = tmp.rename(columns=group_by)

        self.HH.working_MP07bHH_GatherSummary = tmp
