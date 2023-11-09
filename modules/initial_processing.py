import pandas as pd
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
        self.join_static_PollutantCrosswalk_andMetalSpeciations()

        # fmt: off
        self.df["ICFSourceID"] = ""
        set_column(self.df, "ICFCatLevelModeling", self.is_selected_regulatory_code)
        set_column(self.df, "emissions_tpy", self.set_selected_emission_type)
        set_column(self.df, "ICFEmissionProcessGroupAbbr", self.set_epg_abbreviations)
        set_column(self.df, "ICFSourceType", self.set_source_type)
        set_column(self.df, "ICFAreaVolLineReleaseHeight", self.set_release_height)
        self.df["ICFFacilityID"] = self.df["state_county_fips"] + self.df["sppd_facility_identifier"]
        self.df["ICFModelEmissionTPY"] = self.df["emissions_tpy"] * self.df["metal_speciation_factor"]
        self.df["ICFMetal_Speciation_Factor"] = self.df["metal_speciation_factor"]

        # unit conversions
        set_column(self.df, "ICFAreaVolLineReleaseHeight_m", self.release_height_m)
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

    def is_selected_regulatory_code(self, row):
        code = row["regulatory_code"]
        if self.reg_codes and self.reg_codes.get(code) == 1:
            return "Yes"
        return "No"

    def set_selected_emission_type(self, row):
        try:
            colname = f"{config.emission_type.lower()}_emissions_tpy"
            return float(row[colname])
        except:
            raise KeyError(
                "Invalid emissions column name supplied. Rename through config."
            )

    def set_epg_abbreviations(self, row):
        emissions_group = row["emission_process_group"]
        return self.epg_abbr_map.get(emissions_group, "")

    def set_source_type(self, row):
        length = row["fugitive_length_sigmax_ft"]
        width = row["fugitive_width_sigmay_ft"]
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
        erp_type = row["emission_release_point_type"]
        return erp_type_map.get(erp_type, "P")

    def set_release_height(self, row):
        stack_height = row["stack_height (ft)"]
        erp_type = row["emission_release_point_type"]

        if erp_type == "1" or erp_type == "9":
            return stack_height
        elif erp_type == "7":
            return stack_height / 2
        else:
            return 0

    def release_height_m(self, row):
        try:
            release_height_ft = row["ICFAreaVolLineReleaseHeight"]
            return release_height_ft / self.ft_per_m
        except:
            return 0
