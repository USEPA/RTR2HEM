from modules.utils import Join, get_static, calc_agg


def qryMP01a_ListSrcCatFacilities(this):
    group_by = ["ICFFacilityID", "sppd_facility_identifier", "ICFCatLevelModeling"]
    tmp = this.working_crosswalk
    tmp = tmp.loc[tmp["ICFCatLevelModeling"] == "Yes"]

    tmp = tmp.sort_values(group_by)
    tmp = tmp[group_by].drop("ICFCatLevelModeling", axis=1)
    tmp = tmp.drop_duplicates()
    return tmp


# TODO consider in main mp file just running this once with the original working_crosswalk
# so it isnt ran so many times...
def qryMP01b_CountSrcCatFacilities(this):
    src_cat_facilities = qryMP01a_ListSrcCatFacilities(this)
    num_src_cat_facilities = len(src_cat_facilities.index)
    return num_src_cat_facilities


def qryMP02a_ListPBHAPEmittingFacilities01(this):
    group_by = [
        "ICFFacilityID",
        "sppd_facility_identifier",
        "shortpb-hap/ecohapname",
        "ICFCatLevelModeling",
    ]

    pollutant_crosswalk = get_static("static_PollutantCrosswalk_andMetalSpeciations")
    tmp = Join().join(
        [this.working_crosswalk, pollutant_crosswalk], on="pollutant_code"
    )

    tmp = tmp.loc[
        (tmp["shortpb-hap/ecohapname"] != "") & (tmp["ICFCatLevelModeling"] == "Yes")
    ]

    tmp = calc_agg(tmp, group_by, "sum", "emissions_tpy", "SumOfEMISSIONS_TPY")
    tmp = tmp.loc[tmp["SumOfEMISSIONS_TPY"] > 0]
    tmp = tmp.drop_duplicates()

    tmp = tmp.drop("ICFCatLevelModeling", axis=1)
    return tmp


def qryMP02b_ListPBHAPEmittingFacilities02(this):
    group_by = ["ICFFacilityID", "sppd_facility_identifier"]
    pbhap_facilities = qryMP02a_ListPBHAPEmittingFacilities01(this)
    res = pbhap_facilities[group_by].drop_duplicates(group_by)
    return res


# TODO same as above
def qryMP02c_CountPBHAPEmittingFacilities(this):
    num_pbhap_facilities = qryMP02b_ListPBHAPEmittingFacilities02(this)
    num_pbhap_facilities = len(num_pbhap_facilities.index)
    return num_pbhap_facilities
