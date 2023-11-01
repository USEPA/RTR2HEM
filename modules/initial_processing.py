import pandas as pd
from .utils import Join, set_column, get_static, config


class InitialProcessing:
    ft_per_meter = 3.2808399
    fahrenheit_to_kelvin = lambda self, f_temp: ((f_temp - 32) * 0.5555) + 273.15

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

        self.df["ICFSourceID"] = ""
        set_column(self.df, "ICFFacilityID", self.set_icf_facility_id)
        set_column(self.df, "ICFCatLevelModeling", self.is_selected_regulatory_code)
        set_column(self.df, "emissions_tpy", self.set_selected_emission_type)
        set_column(self.df, "ICFModelEmissionTPY", self.set_model_emission_tpy)
        set_column(self.df, "ICFEmissionProcessGroupAbbr", self.set_epg_abbreviations)
        set_column(self.df, "ICFSourceType", self.set_source_type)
        set_column(self.df, "ICFAreaVolLineReleaseHeight", self.set_release_height)
        set_column(
            self.df, "ICFMetal_Speciation_Factor", self.set_metal_speciation_factor
        )

        # unit conversions
        # might not need to store
        set_column(self.df, "ICFStackHeight_m", self.stack_height_meter)
        set_column(self.df, "ICFStackDiameter_m", self.stack_diameter_meter)
        set_column(self.df, "ICFExitGasVelocity_mps", self.gas_velocity_mps)
        set_column(self.df, "ICFExitGasTemperature_K", self.gas_temperature_k)
        set_column(self.df, "ICFFugitiveLength_m", self.fugitive_length_m)
        set_column(self.df, "ICFFugitiveWidth_m", self.fugitive_width_m)
        set_column(self.df, "ICFAreaVolLineReleaseHeight_m", self.release_height_m)

        self.update_by_emission_release_point_type()
        self.df = self.df[self.columns]
        self.df = self.df.fillna("")
        return self.df

    def join_static_PollutantCrosswalk_andMetalSpeciations(self):
        static_pollutantCrosswalk = get_static(
            "static_PollutantCrosswalk_andMetalSpeciations"
        )
        static_pollutantCrosswalk.columns = (
            static_pollutantCrosswalk.columns.str.lower()
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
        self.df.loc[(erp_val != "1") & (erp_val != "7"), update_columns] = ""

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

    def set_icf_facility_id(self, row):
        return row["state_county_fips"] + row["sppd_facility_identifier"]

    def is_selected_regulatory_code(self, row):
        code = row["regulatory_code"]
        if self.reg_codes and self.reg_codes.get(code) == 1:
            return "Yes"
        return "No"

    def set_selected_emission_type(self, row):
        try:
            emissions_df = self.df.filter(
                regex=config.emission_type.lower().replace(" ", "_")
            )
            emissions_col = emissions_df.columns[0]
            return float(row[emissions_col])
        except:
            raise KeyError(
                "Invalid emissions column name supplied. Rename through config."
            )

    def set_model_emission_tpy(self, row):
        return row["emissions_tpy"] * float(row["metal_speciation_factor"])

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

        if erp_type == "1" or erp_type == "7" or erp_type == "9":
            return stack_height
        elif erp_type == "10":
            return stack_height / 2
        else:
            return 0

    def set_metal_speciation_factor(self, row):
        return row["metal_speciation_factor"]

    # unit conversions
    def stack_height_meter(self, row):
        stack_height_ft = row["stack_height (ft)"]
        return stack_height_ft / self.ft_per_meter

    def stack_diameter_meter(self, row):
        stack_diameter_ft = row["stack_diameter (ft)"]
        return stack_diameter_ft / self.ft_per_meter

    def gas_velocity_mps(self, row):
        gas_velocity_fts = row["exit_gas_velocity (ft/sec)"]
        return gas_velocity_fts / self.ft_per_meter

    def gas_temperature_k(self, row):
        gas_temperature_f = row["exit_gas_temperature (f)"]
        return self.fahrenheit_to_kelvin(gas_temperature_f)

    def fugitive_length_m(self, row):
        fugitive_length_f = row["fugitive_length_sigmax_ft"]
        return fugitive_length_f / self.ft_per_meter

    def fugitive_width_m(self, row):
        fugitive_width_f = row["fugitive_width_sigmay_ft"]
        return fugitive_width_f / self.ft_per_meter

    def release_height_m(self, row):
        try:
            release_height_ft = row["ICFAreaVolLineReleaseHeight"]
            return (release_height_ft / self.ft_per_meter) / 2
        except:
            return 0
