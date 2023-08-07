from modules.utils import join, get_static, calc_agg

"""
sheets:
    working_MP07HH_T1Summary
"""


class SummarySetup:
    working_MP07HH_T1Summary = None

    def __init__(self, HH):
        self.HH = HH
        self.qryMP07aHH_PrepareShellOfSummary()

    def qryMP02a_ListPBHAPEmittingFacilities01(self):
        group_by = [
            "ICFFacilityID",
            "sppd_facility_identifier",
            "shortpb-hap/ecohapname",
            "ICFCatLevelModeling",
        ]

        pollutant_crosswalk = get_static(
            "static_PollutantCrosswalk_andMetalSpeciations"
        )
        tmp = join(
            [self.HH.working_crosswalk, pollutant_crosswalk], on="pollutant_code"
        )

        tmp = tmp.loc[
            (tmp["shortpb-hap/ecohapname"] != "")
            & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        tmp = calc_agg(tmp, group_by, "sum", "emissions_tpy", "SumOfEMISSIONS_TPY")
        tmp = tmp.loc[tmp["SumOfEMISSIONS_TPY"] > 0]
        tmp = tmp.drop_duplicates()

        tmp = tmp.drop("ICFCatLevelModeling", axis=1)
        return tmp

    def qryMP02b_ListPBHAPEmittingFacilities02(self):
        group_by = ["ICFFacilityID", "sppd_facility_identifier"]
        pbhap_facilities = self.qryMP02a_ListPBHAPEmittingFacilities01()
        res = pbhap_facilities[group_by].drop_duplicates(group_by)
        return res

    def qryMP02c_CountPBHAPEmittingFacilities(self):
        num_pbhap_facilities = self.qryMP02b_ListPBHAPEmittingFacilities02()
        self.HH.num_pbhap_facilities = len(num_pbhap_facilities.index)
        return self.HH.num_pbhap_facilities

    # working_MP07HH_T1Summary
    def qryMP07aHH_PrepareShellOfSummary(self):
        screen_thresholds = get_static("static_MP_HHScreeningThresholds")
        num_pbhap_facilities = self.qryMP02c_CountPBHAPEmittingFacilities()

        screen_thresholds["Num Facil in Src Cat"] = self.HH.num_src_cat_facilities
        screen_thresholds[
            "Num Facil Emitting Any Assessed PB-HAP"
        ] = num_pbhap_facilities

        blanks_zero = [
            "Num Facil Emitting This PB-HAP",
            "(1)Max SV",
            "(2)Facil-Tot Emis*REF (TPY; facil represented by (1))",
            "(3)Facil-Total Emis (TPY; facil represented by (1))",
            "Num Facil Exceeding",
            "Num Facil Exceeding by x10",
            "Num Facil Exceeding by x100",
        ]
        screen_thresholds[blanks_zero] = 0
        screen_thresholds["Src Cat"] = ""
        screen_thresholds["Max Facility"] = ""

        screen_thresholds = screen_thresholds.sort_values("shortpb-hapname")

        screen_thresholds = screen_thresholds.rename(
            columns={
                "shortpb-hapname": "PB-HAP Grp",
                "tier 1 screening threshold (tpy)": "Tier 1 Scrn Thresh (TPY)",
            }
        )

        self.HH.working_MP07HH_T1Summary = screen_thresholds
