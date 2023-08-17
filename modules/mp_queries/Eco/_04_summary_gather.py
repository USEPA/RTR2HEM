from modules.mp_queries.shared_queries import qryMP02a_ListPBHAPEmittingFacilities01
from modules.utils import Join, get_static, calc_agg

"""
sheets:
    working_MP07eco_T1Summary
    working_MP07eEco_GatherSummary
"""


class SummaryGather:
    def __init__(self, eco):
        self.eco = eco
        self.qryMP07eEco_GatherSummary()

    def qryMP02eEco_ListPBHAPEmittingFacilities01(self):
        """
        SELECT qryMP02a_ListPBHAPEmittingFacilities01.[Facility ID],
        qryMP02a_ListPBHAPEmittingFacilities01.SPPD_FACILITY_IDENTIFIER,
        IIf([qryMP02a_ListPBHAPEmittingFacilities01].[ShortPB-HAP/EcoHAPName]="Methyl Mercury (Hg2)","Mercury",
        [qryMP02a_ListPBHAPEmittingFacilities01].[ShortPB-HAP/EcoHAPName]) AS [ShortPB-HAP/EcoHAPName]

        FROM qryMP02a_ListPBHAPEmittingFacilities01;
        """
        pass

    def qryMP02fEco_ListPBHAPEmittingFacilities02(self):
        """
        SELECT qryMP02eEco_ListPBHAPEmittingFacilities01.[Facility ID], qryMP02eEco_ListPBHAPEmittingFacilities01.SPPD_FACILITY_IDENTIFIER, static_MP_ListOfEcoHAPs.EcoHAP

        FROM qryMP02eEco_ListPBHAPEmittingFacilities01 INNER JOIN static_MP_ListOfEcoHAPs ON qryMP02eEco_ListPBHAPEmittingFacilities01.[ShortPB-HAP/EcoHAPName] = static_MP_ListOfEcoHAPs.EcoHAP_GroupMercury

        GROUP BY qryMP02eEco_ListPBHAPEmittingFacilities01.[Facility ID], qryMP02eEco_ListPBHAPEmittingFacilities01.SPPD_FACILITY_IDENTIFIER, static_MP_ListOfEcoHAPs.EcoHAP;

        """
        pass

    def qryMP02gEco_CountPBHAPEmittingFacilities_ByPBHAP(self):
        """
        SELECT qryMP02fEco_ListPBHAPEmittingFacilities02.EcoHAP AS [EcoHAP Grp],
        Count(qryMP02fEco_ListPBHAPEmittingFacilities02.[Facility ID]) AS [Number of EcoHAP-Emitting Facilities]

        FROM qryMP02fEco_ListPBHAPEmittingFacilities02

        GROUP BY qryMP02fEco_ListPBHAPEmittingFacilities02.EcoHAP;
        """
        group_by = ["shortpb-hap/ecohapname"]
        pbhap_facilities = self.qryMP02fEco_ListPBHAPEmittingFacilities02()

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

    def qryMP06aeco_GetMaxSV(self):
        group_by = ["PB-HAP Grp"]
        max_sv = calc_agg(
            self.eco.working_MP05eco_T1GrpResults, group_by, "max", "SV (grp)", "Max SV"
        )
        return max_sv

    def qryMP06beco_EmissOfMaxSV(self):
        group_by = [
            "PB-HAP Grp",
            "Emiss (TPY; grp)",
            "Emiss*REF (TPY; grp)",
            "SV (grp)",
        ]
        max_sv = self.qryMP06aeco_GetMaxSV()
        res = Join().join(
            [self.eco.working_MP05eco_T1GrpResults, max_sv],
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

    def qryMP06ceco_ListFailingFacilities_PerPBHAP(self):
        group_by = ["PB-HAP Grp", "Facility ID", "SV (grp)", "Exceedance?"]
        res = self.eco.working_MP05eco_T1GrpResults[group_by]
        res = res.loc[res["Exceedance?"] == "Yes"]
        return res

    def qryMP06deco_CountFailingFacilities_PerPBHAP(self):
        group_by = ["PB-HAP Grp"]
        exceed = self.qryMP06ceco_ListFailingFacilities_PerPBHAP()
        res = calc_agg(exceed, group_by, "count", "Facility ID", "Num Facil Exceeding")
        return res

    def qryMP06eeco_ListFailingFacilitiesx10_PerPBHAP(self):
        group_by = ["PB-HAP Grp", "Facility ID", "SV (grp)", "Exceedance by x10?"]
        res = self.eco.working_MP05eco_T1GrpResults[group_by]
        res = res.loc[res["Exceedance by x10?"] == "Yes"]
        return res

    def qryMP06feco_CountFailingFacilitiesx10_PerPBHAP(self):
        group_by = ["PB-HAP Grp"]
        exceed = self.qryMP06eeco_ListFailingFacilitiesx10_PerPBHAP()
        res = calc_agg(
            exceed, group_by, "count", "Facility ID", "Num Facil Exceeding by x10"
        )
        return res

    def qryMP06geco_ListFailingFacilitiesx100_PerPBHAP(self):
        group_by = ["PB-HAP Grp", "Facility ID", "SV (grp)", "Exceedance by x100?"]
        res = self.eco.working_MP05eco_T1GrpResults[group_by]
        res = res.loc[res["Exceedance by x100?"] == "Yes"]
        return res

    def qryMP06ecoH_CountFailingFacilitiesx100_PerPBHAP(self):
        group_by = ["PB-HAP Grp"]
        exceed = self.qryMP06geco_ListFailingFacilitiesx100_PerPBHAP()
        res = calc_agg(
            exceed, group_by, "count", "Facility ID", "Num Facil Exceeding by x100"
        )
        return res

    # working_MP07eco_T1Summary, working_MP07eEco_GatherSummary
    def qryMP07eEco_GatherSummary(self):
        """
        SELECT working_MP07Eco_T1Summary.[Src Cat],
        working_MP07Eco_T1Summary.[EcoHAP Grp],
        qryMP02gEco_CountPBHAPEmittingFacilities_ByPBHAP.[Number of EcoHAP-Emitting Facilities] AS [Num Facil Emitting This PB-HAP],
        working_MP07Eco_T1Summary.[Assessment Endpoint],
        qryMP06jEco_EmissOfMaxSV.[Max Emiss*EcoEEF (TPY; grp)] AS [(2)Facil-Tot Emis*EcoEF (TPY; facil represented by (1))],
        qryMP06jEco_EmissOfMaxSV.[Emiss (TPY; grp)] AS [(3)Facil-Total Emis (TPY; facil represented by (1))],
        qryMP06jEco_EmissOfMaxSV.[Benchmark Effects Level],
        qryMP06jEco_EmissOfMaxSV.[Benchmark Value],
        qryMP06jEco_EmissOfMaxSV.[Max SV] AS [(1)Max SV],
        qryMP06jEco_EmissOfMaxSV.[Facil ID],
        Nz([qryMP06lEco_CountFailingFacilities_PerPBHAP].[Num Facil Exceeding],0) AS [Num Facil Exceeding],
        Nz([qryMP06nEco_CountFailingFacilitiesx10_PerPBHAP].[Num Facil Exceeding by x10],0) AS [Num Facil Exceeding by x10]
        INTO working_MP07eEco_GatherSummary

        FROM (((working_MP07Eco_T1Summary
        INNER JOIN qryMP02gEco_CountPBHAPEmittingFacilities_ByPBHAP
        ON working_MP07Eco_T1Summary.[EcoHAP Grp] = qryMP02gEco_CountPBHAPEmittingFacilities_ByPBHAP.[EcoHAP Grp])
        LEFT JOIN qryMP06lEco_CountFailingFacilities_PerPBHAP
        ON (working_MP07Eco_T1Summary.[Assessment Endpoint] = qryMP06lEco_CountFailingFacilities_PerPBHAP.[Assessment Endpoint])
        AND (working_MP07Eco_T1Summary.[EcoHAP Grp] = qryMP06lEco_CountFailingFacilities_PerPBHAP.[EcoHAP Grp])
        AND (working_MP07Eco_T1Summary.[Benchmark Effects Level] = qryMP06lEco_CountFailingFacilities_PerPBHAP.[Benchmark Effects Level]))
        LEFT JOIN qryMP06nEco_CountFailingFacilitiesx10_PerPBHAP
        ON (working_MP07Eco_T1Summary.[Assessment Endpoint] = qryMP06nEco_CountFailingFacilitiesx10_PerPBHAP.[Assessment Endpoint])
        AND (working_MP07Eco_T1Summary.[EcoHAP Grp] = qryMP06nEco_CountFailingFacilitiesx10_PerPBHAP.[EcoHAP Grp])
        AND (working_MP07Eco_T1Summary.[Benchmark Effects Level] = qryMP06nEco_CountFailingFacilitiesx10_PerPBHAP.[Benchmark Effects Level]))
        LEFT JOIN qryMP06jEco_EmissOfMaxSV ON (working_MP07Eco_T1Summary.[EcoHAP Grp] = qryMP06jEco_EmissOfMaxSV.[EcoHAP Grp])
        AND (working_MP07Eco_T1Summary.[Assessment Endpoint] = qryMP06jEco_EmissOfMaxSV.[Assessment Endpoint])
        AND (working_MP07Eco_T1Summary.[Benchmark Effects Level] = qryMP06jEco_EmissOfMaxSV.[Benchmark Effects Level])

        GROUP BY working_MP07Eco_T1Summary.[Src Cat],
        working_MP07Eco_T1Summary.[EcoHAP Grp],
        qryMP02gEco_CountPBHAPEmittingFacilities_ByPBHAP.[Number of EcoHAP-Emitting Facilities],
        working_MP07Eco_T1Summary.[Assessment Endpoint],
        qryMP06jEco_EmissOfMaxSV.[Max Emiss*EcoEEF (TPY; grp)],
        qryMP06jEco_EmissOfMaxSV.[Emiss (TPY; grp)],
        qryMP06jEco_EmissOfMaxSV.[Benchmark Effects Level],
        qryMP06jEco_EmissOfMaxSV.[Benchmark Value],
        qryMP06jEco_EmissOfMaxSV.[Max SV],
        qryMP06jEco_EmissOfMaxSV.[Facil ID],
        Nz([qryMP06lEco_CountFailingFacilities_PerPBHAP].[Num Facil Exceeding],0),
        Nz([qryMP06nEco_CountFailingFacilitiesx10_PerPBHAP].[Num Facil Exceeding by x10],0);
        """
        num_pbhap_facil = self.qryMP02gEco_CountPBHAPEmittingFacilities_ByPBHAP()
        max_sv_emiss = self.qryMP06beco_EmissOfMaxSV()
        count_failing_facil = self.qryMP06deco_CountFailingFacilities_PerPBHAP()
        count_failing_facil_10x = self.qryMP06feco_CountFailingFacilitiesx10_PerPBHAP()
        count_failing_facil_100x = (
            self.qryMP06ecoH_CountFailingFacilitiesx100_PerPBHAP()
        )

        tmp = Join().join(
            [self.eco.working_MP07eco_T1Summary, num_pbhap_facil],
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

        self.eco.working_MP07eEco_GatherSummary = tmp
