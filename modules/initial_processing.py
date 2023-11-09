import numpy as np
from .utils import Join, set_column, get_static, config


class InitialProcessing:
    ft_per_m = 3.2808399
    f_to_k = lambda self, f_temp: ((f_temp - 32) * 0.5555) + 273.15

    columns = [
        "ICFFacilityID",
        "sppd_facility_identifier",
        "ICFSourceID",
        "ICFSourceType",
        "pollutant_code",
        "pollutant_description",
        "hap_category_name",
        "hem3_chemical_name",
        "chem name for tier 2 tool",
        "emissions_tpy",
        "ICFModelEmissionTPY",
        "regulatory_code",
        "ICFCatLevelModeling",
        "emission_process_group",
        "ICFEmissionProcessGroupAbbr",
        "emission_unit_id",
        "process_id",
        "emission_release_point_id",
        "emission_release_point_type",
        "scc",
        "naics_primary",
        "y_coordinate",
        "x_coordinate",
        "fugitive_2d_midpoint1_x_coordinate",
        "fugitive_2d_midpoint1_y_coordinate",
        "fugitive_2d_midpoint2_x_coordinate",
        "fugitive_2d_midpoint2_y_coordinate",
        "ICFAreaVolLineReleaseHeight_m",
        "ICFStackHeight_m",
        "ICFExitGasTemperature_K",
        "ICFStackDiameter_m",
        "ICFExitGasVelocity_mps",
        "ICFFugitiveLength_m",
        "ICFFugitiveWidth_m",
        "fugitive_angle_degrees",
        "ICFMetal_Speciation_Factor",
        "facility_name",
        "location_address",
        "city",
        "county_name",
        "state_abbr",
        "zipcode",
    ]

    def __init__(self, df, epgs, reg_codes):
        self.df = df
        self.epg_abbr_map = epgs
        self.reg_codes = reg_codes

    def run(self):
        emis_type = f"{config.emission_type.lower()}_emissions_tpy"
        self.join_static_PollutantCrosswalk_andMetalSpeciations()

        """
        would like to make more readable
        maybe revisit vset_column...but slightly different approach
        is it really slow to include every column..?
        """

        # fmt: off
        self.df["ICFSourceID"] = ""
        self.df["ICFCatLevelModeling"] = is_selected_regulatory_code(self.reg_codes, self.df["regulatory_code"])
        self.df["emissions_tpy"] = set_selected_emission_type(self.df[emis_type])
        self.df["ICFEmissionProcessGroupAbbr"] = set_epg_abbreviations(self.epg_abbr_map, self.df["emission_process_group"])
        self.df["ICFSourceType"] = set_source_type(self.df["fugitive_length_sigmax_ft"], self.df["fugitive_width_sigmay_ft"], self.df["emission_release_point_type"])
        self.df["ICFAreaVolLineReleaseHeight"] = set_release_height(self.df["stack_height (ft)"], self.df["emission_release_point_type"])

        self.df["ICFFacilityID"] = self.df["state_county_fips"] + self.df["sppd_facility_identifier"]
        self.df["ICFModelEmissionTPY"] = self.df["emissions_tpy"] * self.df["metal_speciation_factor"]
        self.df["ICFMetal_Speciation_Factor"] = self.df["metal_speciation_factor"]

        # unit conversions
        self.df["ICFAreaVolLineReleaseHeight_m"] = release_height_m(self.ft_per_m, self.df["ICFAreaVolLineReleaseHeight"])
        self.df["ICFStackHeight_m"] = self.df["stack_height (ft)"] / self.ft_per_m
        self.df["ICFStackDiameter_m"] = self.df["stack_diameter (ft)"] / self.ft_per_m
        self.df["ICFExitGasVelocity_mps"] = self.df["exit_gas_velocity (ft/sec)"] / self.ft_per_m
        self.df["ICFExitGasTemperature_K"] = self.f_to_k(self.df["exit_gas_temperature (f)"])
        self.df["ICFFugitiveLength_m"] = self.df["fugitive_length_sigmax_ft"] / self.ft_per_m
        self.df["ICFFugitiveWidth_m"] = self.df["fugitive_width_sigmay_ft"] / self.ft_per_m
        # fmt: on

        self.update_by_emission_release_point_type()
        self.df = self.df[self.columns]
        self.df = self.df.fillna("")
        return self.df

    def join_static_PollutantCrosswalk_andMetalSpeciations(self):
        static_pollutantCrosswalk = get_static(
            "static_PollutantCrosswalk_andMetalSpeciations"
        )
        self.df = Join().join(
            [self.df, static_pollutantCrosswalk],
            on="pollutant_code",
            how="inner",
        )

    def update_by_emission_release_point_type(self):
        """Some columns should be empty based on emission release point type"""
        erp_val = self.df["emission_release_point_type"]

        update_columns = ["ICFAreaVolLineReleaseHeight_m", "ICFFugitiveWidth_m"]
        self.df.loc[
            (erp_val != "1") & (erp_val != "7") & (erp_val != "9") & (erp_val != "10"),
            update_columns,
        ] = ""

        update_columns = ["ICFFugitiveLength_m", "fugitive_angle_degrees"]
        # self.df.loc[(erp_val != "1") & (erp_val != "7"), update_columns] = ""
        self.df.loc[(erp_val != "1"), update_columns] = ""

        update_columns = [
            "ICFStackHeight_m",
            "ICFExitGasTemperature_K",
            "ICFStackDiameter_m",
            "ICFExitGasVelocity_mps",
        ]
        self.df.loc[
            (erp_val == "1") | (erp_val == "7") | (erp_val == "9") | (erp_val == "10"),
            update_columns,
        ] = ""


@np.vectorize
def is_selected_regulatory_code(all_codes, code):
    if all_codes and all_codes.get(code) == 1:
        return "Yes"
    return "No"


@np.vectorize
def set_selected_emission_type(val):
    try:
        return float(val)
    except:
        raise KeyError("Invalid emissions column name supplied. Rename through config.")


@np.vectorize
def set_epg_abbreviations(epg_abbr_map, epg):
    return epg_abbr_map.get(epg, "")


@np.vectorize
def set_source_type(length, width, erp_type):
    erp_type_map = {
        "1": "A" if length > 0 and width > 0 else "P",  # area
        "2": "P",
        "3": "H",  # horizontal
        "4": "H",  # horizontal
        "5": "C",  # capped
        "6": "H",  # horizontal
        "7": "V",  # volume
        "8": "P",
        "9": "N",  # line
    }
    return erp_type_map.get(erp_type, "P")


@np.vectorize
def set_release_height(stack_height, erp_type):
    if erp_type == "1" or erp_type == "9":
        return stack_height
    elif erp_type == "7":
        return stack_height / 2
    else:
        return 0


@np.vectorize
def release_height_m(ft_per_m, release_height_ft):
    try:
        return release_height_ft / ft_per_m
    except:
        return 0
