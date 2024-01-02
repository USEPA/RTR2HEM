from src.utils import Join, get_static, calc_agg, config


def split_by_reg_codes(this):
    """Returns data split between selected and not selected regulatory codes"""
    out_codes = [k for k, v in config.reg_codes.items() if v == 0]
    in_codes = [k for k, v in config.reg_codes.items() if v == 1]

    out_res = this.df.loc[this.df["regulatory_code"].isin(out_codes)]
    in_res = this.df.loc[this.df["regulatory_code"].isin(in_codes)]

    out_res.loc[:, "regulatory_code"] = "OUTSIDE SOURCE CATEGORY"
    in_res.loc[:, "regulatory_code"] = "INSIDE SOURCE CATEGORY"
    return out_res, in_res


def qry_01a_ListSrcCatFacilities(this):
    group_by = ["ICFFacilityID", "sppd_facility_identifier", "ICFCatLevelModeling"]
    tmp = this.working_crosswalk
    tmp = tmp.loc[tmp["ICFCatLevelModeling"] == "Yes"]

    tmp = tmp.sort_values(group_by)
    tmp = tmp[group_by].drop("ICFCatLevelModeling", axis=1)
    tmp = tmp.drop_duplicates()
    return tmp


# TODO consider in main mp file just running this once with the original working_crosswalk
# so it isnt ran so many times...
def qry_01b_CountSrcCatFacilities(this):
    src_cat_facilities = qry_01a_ListSrcCatFacilities(this)
    num_src_cat_facilities = len(src_cat_facilities.index)
    return num_src_cat_facilities


def qry_02a_ListPBHAPEmittingFacilities01(this):
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


def qry_02b_ListPBHAPEmittingFacilities02(this):
    group_by = ["ICFFacilityID", "sppd_facility_identifier"]
    pbhap_facilities = qry_02a_ListPBHAPEmittingFacilities01(this)
    res = pbhap_facilities[group_by].drop_duplicates(group_by)
    return res


# TODO same as above
def qry_02c_CountPBHAPEmittingFacilities(this):
    num_pbhap_facilities = qry_02b_ListPBHAPEmittingFacilities02(this)
    num_pbhap_facilities = len(num_pbhap_facilities.index)
    return num_pbhap_facilities
