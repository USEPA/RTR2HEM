from .utils import emission_type

"""
Next steps:
''ADD SOME NEW FIELDS TO THE EMISSION INVENTORY, IDENTIFY THE DESIRED EMISSIONS FIELD,
''POPULATE EPGROUP ABBREVIATIONS, CONVERT TO METRIC, IDENTIFY AERMOD SOURCE TYPES,
''CREATE STATE GROUPS AS NEEDED FOR FILE SIZE CONSTRAINTS -
''CREATE CROSSWALK FILE

uses:
    table "input_EmissionInventory_withICFWork"
"""


class InitialProcessing:
    ft_per_meter = 3.2808399
    fahrenheit_to_kelvin = lambda self, f_temp: ((f_temp - 32) * 0.5555) + 273.15

    def __init__(self, df, epgs, reg_codes=None):
        self.df = df
        self.epg_abbr_map = epgs
        self.reg_codes = reg_codes

    def set_column(self, column_name, func):
        self.df[column_name] = self.df.apply(lambda row: func(row), axis=1)

    def run(self):
        self.set_column("ICFFacilityID", self.set_icf_facility_id)
        self.set_column(
            "ICFCatLevelModeling", self.is_selected_regulatory_code
        )  # todo probably rename column
        self.set_column("EMISSIONS_TPY", self.set_selected_emission_type)
        self.set_column("ICFEmissionProcessGroupAbbr", self.set_epg_abbreviations)
        self.set_column("ICFSourceType", self.set_source_type)
        self.set_column("ICFAreaVolLineReleaseHeight", self.set_release_height)

        # unit conversions
        # consider cutting out, probably dont need to store
        self.set_column("ICFStackHeight_m", self.stack_height_meter)
        self.set_column("ICFStackDiameter_m", self.stack_diameter_meter)
        self.set_column("ICFExitGasVelocity_mps", self.gas_velocity_mps)
        self.set_column("ICFExitGasTemperature_K", self.gas_temperature_k)
        self.set_column("ICFFugitiveLength_m", self.fugitive_length_m)
        self.set_column("ICFFugitiveWidth_m", self.fugitive_width_m)
        self.set_column("ICFAreaVolLineReleaseHeight_m", self.release_height_m)

        return self.df

    def set_icf_facility_id(self, row):
        return row["state_county_fips"] + row["sppd_facility_identifier"]

    def is_selected_regulatory_code(self, row):
        code = row["regulatory_code"]
        if self.reg_codes == None:
            return True
        return self.reg_codes.get(code, False) == 1

    def set_selected_emission_type(self, row):
        try:
            emissions_df = self.df.filter(regex=emission_type.lower().replace(" ", "_"))
            emissions_col = emissions_df.columns[0]
            return row[emissions_col]
        except:
            raise KeyError(
                "Invalid emissions column name supplied. Rename through config."
            )

    def set_epg_abbreviations(self, row):
        emissions_group = row["emission_process_group"]
        return self.epg_abbr_map.get(emissions_group, "")

    def set_source_type(self, row):
        """
        TODO -- double check, although everything in this example run should be "P"
        """
        length = int(row["fugitive_length_sigmax_ft"])
        width = int(row["fugitive_width_sigmay_ft"])
        erp_type_map = {
            "1": "A" if length > 0 and width > 0 else "P",  # area
            "2": "P",
            "3": "H",  # horizontal
            "4": "H",  # horizontal
            "5": "C",  # capped
            "6": "H",  # horizontal
            "7": "A",  # area
            "8": "P",
            "9": "N",  # line
            "10": "V",  # volume
        }
        erp_type = row["emission_release_point_type"]
        return erp_type_map.get(erp_type, "P")

    def set_release_height(self, row):
        stack_height = row["stack_height (ft)"]
        erp_type = row["emission_release_point_type"]

        if erp_type == "1" or erp_type == "7" or erp_type == "9":
            return float(stack_height)
        elif erp_type == "10":
            return float(stack_height) / 2
        else:
            return ""

    # unit conversions
    def stack_height_meter(self, row):
        stack_height_ft = float(row["stack_height (ft)"])
        return stack_height_ft / self.ft_per_meter

    def stack_diameter_meter(self, row):
        stack_diameter_ft = float(row["stack_diameter (ft)"])
        return stack_diameter_ft / self.ft_per_meter

    def gas_velocity_mps(self, row):
        fts_gas_velocity = float(row["exit_gas_velocity (ft/sec)"])
        return fts_gas_velocity / self.ft_per_meter

    def gas_temperature_k(self, row):
        gas_temperature_f = float(row["exit_gas_temperature (f)"])
        return self.fahrenheit_to_kelvin(gas_temperature_f)

    def fugitive_length_m(self, row):
        fugitive_length_f = float(row["fugitive_length_sigmax_ft"])
        return fugitive_length_f / self.ft_per_meter

    def fugitive_width_m(self, row):
        fugitive_width_f = float(row["fugitive_width_sigmay_ft"])
        return fugitive_width_f / self.ft_per_meter

    # what to do if ICFAreaVolLineReleaseHeight is null
    def release_height_m(self, row):
        try:
            release_height_ft = float(row["ICFAreaVolLineReleaseHeight"])
            return release_height_ft / self.ft_per_meter
        except:
            return ""
