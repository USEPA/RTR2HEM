from modules.mp_queries.HH._03_summary_setup import SummarySetup
from modules.utils import join, get_static, calc_agg

"""
sheets:
    working_MP07bHH_GatherSummary
"""


class SummaryGather:
    working_MP07bHH_GatherSummary = None

    def __init__(self, HH):
        self.HH = HH
        self.qryMP07bHH_GatherSummary()

    def qryMP02dHH_CountPBHAPEmittingFacilities_ByPBHAP(self):
        group_by = ["shortpb-hap/ecohapname"]
        pbhap_facilities = SummarySetup(
            self.HH
        ).qryMP02a_ListPBHAPEmittingFacilities01()

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

    def qryMP06aHH_GetMaxSV(self):
        group_by = ["PB-HAP Grp"]
        max_sv = calc_agg(
            self.HH.working_MP05HH_T1GrpResults, group_by, "max", "SV (grp)", "Max SV"
        )
        return max_sv

    def qryMP06bHH_EmissOfMaxSV(self):
        group_by = [
            "PB-HAP Grp",
            "Emiss (TPY; grp)",
            "Emiss*REF (TPY; grp)",
            "SV (grp)",
        ]
        max_sv = self.qryMP06aHH_GetMaxSV()
        res = join(
            [self.HH.working_MP05HH_T1GrpResults, max_sv],
            how="inner",
            left_on=["PB-HAP Grp", "SV (grp)"],
            right_on=["PB-HAP Grp", "Max SV"],
        )

        res = res.sort_values("Facility ID")
        res = res[group_by + ["Facility ID"]].drop_duplicates(group_by)
        res = res.rename(columns={"Facility ID": "Facil ID"})
        return res

    def qryMP06dHH_CountFailingFacilities_PerPBHAP(self):
        pass

    def qryMP06fHH_CountFailingFacilitiesx10_PerPBHAP(self):
        pass

    def qryMP06hHH_CountFailingFacilitiesx100_PerPBHAP(self):
        pass

    # working_MP07bHH_GatherSummary
    def qryMP07bHH_GatherSummary(self):
        """
        NOTE -- https://support.microsoft.com/en-au/office/nz-function-8ef85549-cc9c-438b-860a-7fd9f4c69b6c

        SELECT working_MP07HH_T1Summary.[Src Cat],
        working_MP07HH_T1Summary.[PB-HAP Grp],
        qryMP02dHH_CountPBHAPEmittingFacilities_ByPBHAP.[Num Facil Emitting This PB-HAP],
        qryMP06bHH_EmissOfMaxSV.[Max Emiss*REF (TPY; grp)] AS [(2)Facil-Tot Emis*REF (TPY; facil represented by (1))],
        qryMP06bHH_EmissOfMaxSV.[Max Emiss*REF (TPY; grp)] AS [(3)Facil-Total Emis (TPY; facil represented by (1))],
        qryMP06bHH_EmissOfMaxSV.[Max SV (grp)] AS [(1)Max SV],
        qryMP06bHH_EmissOfMaxSV.[Facil ID] AS [Max Facility],
        Nz([qryMP06dHH_CountFailingFacilities_PerPBHAP].[Num Facil Exceeding],0) AS [Num Facil Exceeding],
        Nz([qryMP06fHH_CountFailingFacilitiesx10_PerPBHAP].[Num Facil Exceeding by x10],0) AS [Num Facil Exceeding by x10],
        Nz([qryMP06hHH_CountFailingFacilitiesx100_PerPBHAP].[Num Facil Exceeding by x100],0) AS [Num Facil Exceeding by x100]
        INTO working_MP07bHH_GatherSummary

        FROM ((((working_MP07HH_T1Summary
        INNER JOIN qryMP02dHH_CountPBHAPEmittingFacilities_ByPBHAP
        ON working_MP07HH_T1Summary.[PB-HAP Grp] = qryMP02dHH_CountPBHAPEmittingFacilities_ByPBHAP.[PB-HAP Grp])
        LEFT JOIN qryMP06dHH_CountFailingFacilities_PerPBHAP
        ON working_MP07HH_T1Summary.[PB-HAP Grp] = qryMP06dHH_CountFailingFacilities_PerPBHAP.[PB-HAP Grp])
        LEFT JOIN qryMP06fHH_CountFailingFacilitiesx10_PerPBHAP
        ON working_MP07HH_T1Summary.[PB-HAP Grp] = qryMP06fHH_CountFailingFacilitiesx10_PerPBHAP.[PB-HAP Grp])
        LEFT JOIN qryMP06hHH_CountFailingFacilitiesx100_PerPBHAP
        ON working_MP07HH_T1Summary.[PB-HAP Grp] = qryMP06hHH_CountFailingFacilitiesx100_PerPBHAP.[PB-HAP Grp])
        LEFT JOIN qryMP06bHH_EmissOfMaxSV ON working_MP07HH_T1Summary.[PB-HAP Grp] = qryMP06bHH_EmissOfMaxSV.[PB-HAP Grp]

        GROUP BY working_MP07HH_T1Summary.[Src Cat],
        working_MP07HH_T1Summary.[PB-HAP Grp],
        qryMP02dHH_CountPBHAPEmittingFacilities_ByPBHAP.[Num Facil Emitting This PB-HAP],
        qryMP06bHH_EmissOfMaxSV.[Max Emiss*REF (TPY; grp)], qryMP06bHH_EmissOfMaxSV.[Max SV (grp)],
        qryMP06bHH_EmissOfMaxSV.[Facil ID], Nz([qryMP06dHH_CountFailingFacilities_PerPBHAP].[Num Facil Exceeding],0),
        Nz([qryMP06fHH_CountFailingFacilitiesx10_PerPBHAP].[Num Facil Exceeding by x10],0),
        Nz([qryMP06hHH_CountFailingFacilitiesx100_PerPBHAP].[Num Facil Exceeding by x100],0),
        qryMP06bHH_EmissOfMaxSV.[Max Emiss*REF (TPY; grp)];
        """
        self.qryMP02dHH_CountPBHAPEmittingFacilities_ByPBHAP()
        self.qryMP06bHH_EmissOfMaxSV()
        pass
