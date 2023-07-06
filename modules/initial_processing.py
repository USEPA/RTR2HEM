import pandas as pd
import numpy as np
from .utils import (
    get_xls_sheet,
    get_col,
    emission_type,
    postprocessing_columns,
)


"""
"SELECT input_EmissionInventory_withICFWork.StateGroup, 
        input_EmissionInventory_withICFWork.ICFFacilityID, 
        input_EmissionInventory_withICFWork.SPPD_FACILITY_IDENTIFIER, 
        input_EmissionInventory_withICFWork.ICFSourceID, 
        input_EmissionInventory_withICFWork.ICFSourceType, 
        input_EmissionInventory_withICFWork.POLLUTANT_CODE, 
        input_EmissionInventory_withICFWork.POLLUTANT_DESCRIPTION,
        input_EmissionInventory_withICFWork.HAP_CATEGORY_NAME, 

        input_EmissionInventory_withICFWork.EMISSIONS_TPY, 
        ([Emissions_TPY]*[Metal_Speciation_Factor]) AS ICFModelEmissionTPY, '' AS blank, " _        --> metal speciation is in static_crosswalk
        
        static_PollutantCrosswalk_andMetalSpeciations.HEM3_Chemical_Name, 
        static_PollutantCrosswalk_andMetalSpeciations.[Chem Name For Tier 2 Tool], 

        & "input_EmissionInventory_withICFWork.REGULATORY_CODE , 
        input_EmissionInventory_withICFWork.ICFCatLevelModeling, 
        input_EmissionInventory_withICFWork.EMISSION_PROCESS_GROUP, 
        input_EmissionInventory_withICFWork.ICFEmissionProcessGroupAbbr, " _

        & "input_EmissionInventory_withICFWork.EMISSION_UNIT_ID, 
        input_EmissionInventory_withICFWork.PROCESS_ID, 
        input_EmissionInventory_withICFWork.EMISSION_RELEASE_POINT_ID, 
        input_EmissionInventory_withICFWork.EMISSION_RELEASE_POINT_TYPE, 
        input_EmissionInventory_withICFWork.SCC, 
        input_EmissionInventory_withICFWork.NAICS_PRIMARY, 
        '' AS blank2, 
        input_EmissionInventory_withICFWork.Y_COORDINATE, 
        input_EmissionInventory_withICFWork.X_COORDINATE, " _

        & "input_EmissionInventory_withICFWork.FUGITIVE_2D_MIDPOINT1_X_COORDINATE, 
        input_EmissionInventory_withICFWork.FUGITIVE_2D_MIDPOINT1_Y_COORDINATE, 
        input_EmissionInventory_withICFWork.FUGITIVE_2D_MIDPOINT2_X_COORDINATE, 
        input_EmissionInventory_withICFWork.FUGITIVE_2D_MIDPOINT2_Y_COORDINATE, " _

        ------------LOGIC STARTS HERE------------

        & "IIf([input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'1' And 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'7' And 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'9' And 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'10',Null,[input_EmissionInventory_withICFWork]![ICFAreaVolLineReleaseHeight_m]) AS ICFAreaVolLineReleaseHeight_m, " _

        & "IIf([input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='1' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='7' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='9' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='10',Null,[input_EmissionInventory_withICFWork]![ICFStackHeight_m]) AS ICFStackHeight_m, " _

        & "IIf([input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='1' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='7' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='9' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='10',Null,[input_EmissionInventory_withICFWork]![ICFExitGasTemperature_K]) AS ICFExitGasTemperature_K, " _

        & "IIf([input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='1' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='7' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='9' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='10',Null,[input_EmissionInventory_withICFWork]![ICFStackDiameter_m]) AS ICFStackDiameter_m, " _

        & "IIf([input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='1' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='7' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='9' Or 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]='10',Null,[input_EmissionInventory_withICFWork]![ICFExitGasVelocity_mps]) AS ICFExitGasVelocity_mps, " _

        & "IIf([input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'1' And 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'7',Null,[input_EmissionInventory_withICFWork]![ICFFugitiveLength_m]) AS ICFFugitiveLength_m, " _

        & "IIf([input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'1' And 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'7' And 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'9' And 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'10',Null,[input_EmissionInventory_withICFWork]![ICFFugitiveWidth_m]) AS ICFFugitiveWidth_m, " _

        & "IIf([input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'1' And 
        [input_EmissionInventory_withICFWork]![EMISSION_RELEASE_POINT_TYPE]<>'7',Null,[input_EmissionInventory_withICFWork]![FUGITIVE_ANGLE_DEGREES]) AS FUGITIVE_ANGLE_DEGREES, " _

        ------------LOGIC ENDS HERE------------

        & "'' AS blank3, static_PollutantCrosswalk_andMetalSpeciations.Metal_Speciation_Factor AS ICFMetal_Speciation_Factor, " _
        & "'' AS blank4, input_EmissionInventory_withICFWork.FACILITY_NAME, input_EmissionInventory_withICFWork.LOCATION_ADDRESS, input_EmissionInventory_withICFWork.CITY, " _
        & "input_EmissionInventory_withICFWork.COUNTY_NAME, input_EmissionInventory_withICFWork.STATE_ABBR, input_EmissionInventory_withICFWork.ZIPCODE " _
        & "INTO working_CrosswalkEmissionInventory " _
        
        & "FROM input_EmissionInventory_withICFWork INNER JOIN 
        static_PollutantCrosswalk_andMetalSpeciations ON 
        input_EmissionInventory_withICFWork.POLLUTANT_CODE=static_PollutantCrosswalk_andMetalSpeciations.Pollutant_Code;"
"""

"""
NOTE
    "StateGroup" is not created as that step is currently skipped
    "ICFSourceID" not yet created
    "blank", "blank2", "blank3", "blank4" not yet created

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

    # excel has a cap on max sheet name length
    # temp replace 'static_PollutantCrosswalk_andMetalSpeciations' with 'static_PollutantCrosswalk_andMe'
    def join_static_PollutantCrosswalk_andMetalSpeciations(self):
        static_pollutantCrosswalk = get_xls_sheet("static_PollutantCrosswalk_andMe")
        static_pollutantCrosswalk.columns = (
            static_pollutantCrosswalk.columns.str.lower()
        )
        self.df = pd.merge(
            self.df,
            static_pollutantCrosswalk,
            on="pollutant_code",
            how="inner",
            suffixes=("", "_y"),
        )

    def drop_unneeded_columns(self):
        lower_preprocessed = [w.lower() for w in postprocessing_columns]
        for c in self.df.columns:
            if c.lower() not in lower_preprocessed:
                self.df = self.df.drop(c, axis=1)

    def update_by_emission_release_point_type(self):
        """Some columns should be empty based on emission release point type"""
        erp_val = self.df[get_col("emission_release_point_type")]

        update_columns = ["ICFAreaVolLineReleaseHeight_m", "ICFFugitiveWidth_m"]
        self.df.loc[
            (erp_val != "1") & (erp_val != "7") & (erp_val != "9") & (erp_val != "10"),
            update_columns,
        ] = ""
        
        update_columns = ["ICFFugitiveLength_m", get_col("fugitive_angle_degrees")]
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

    def run(self):
        self.join_static_PollutantCrosswalk_andMetalSpeciations()

        self.set_column("ICFFacilityID", self.set_icf_facility_id)
        self.set_column("ICFCatLevelModeling", self.is_selected_regulatory_code)
        self.set_column("EMISSIONS_TPY", self.set_selected_emission_type)
        self.set_column("ICFModelEmissionTPY", self.set_model_emission_tpy)
        self.set_column("ICFEmissionProcessGroupAbbr", self.set_epg_abbreviations)
        self.set_column("ICFSourceType", self.set_source_type)
        self.set_column("ICFAreaVolLineReleaseHeight", self.set_release_height)
        self.set_column("ICFMetal_Speciation_Factor", self.set_metal_speciation_factor)

        # unit conversions
        # might not need to store
        self.set_column("ICFStackHeight_m", self.stack_height_meter)
        self.set_column("ICFStackDiameter_m", self.stack_diameter_meter)
        self.set_column("ICFExitGasVelocity_mps", self.gas_velocity_mps)
        self.set_column("ICFExitGasTemperature_K", self.gas_temperature_k)
        self.set_column("ICFFugitiveLength_m", self.fugitive_length_m)
        self.set_column("ICFFugitiveWidth_m", self.fugitive_width_m)
        self.set_column("ICFAreaVolLineReleaseHeight_m", self.release_height_m)

        self.update_by_emission_release_point_type()
        self.drop_unneeded_columns()
        self.df = self.df.fillna("")
        return self.df

    def set_icf_facility_id(self, row):
        return get_col("state_county_fips", row) + get_col(
            "sppd_facility_identifier", row
        )

    def is_selected_regulatory_code(self, row):
        code = get_col("regulatory_code", row)
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

    def set_model_emission_tpy(self, row):
        return float(row["EMISSIONS_TPY"]) * float(
            get_col("metal_speciation_factor", row)
        )

    def set_epg_abbreviations(self, row):
        emissions_group = get_col("emission_process_group", row)
        return self.epg_abbr_map.get(emissions_group, "")

    def set_source_type(self, row):
        """
        TODO -- double check, although everything in this example run should be "P"
        """
        length = int(get_col("fugitive_length_sigmax_ft", row))
        width = int(get_col("fugitive_width_sigmay_ft", row))
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
        erp_type = get_col("emission_release_point_type", row)
        return erp_type_map.get(erp_type, "P")

    def set_release_height(self, row):
        stack_height = get_col("stack_height (ft)", row)
        erp_type = get_col("emission_release_point_type", row)

        if erp_type == "1" or erp_type == "7" or erp_type == "9":
            return float(stack_height)
        elif erp_type == "10":
            return float(stack_height) / 2
        else:
            return ""

    def set_metal_speciation_factor(self, row):
        return get_col("metal_speciation_factor", row)

    # unit conversions
    def stack_height_meter(self, row):
        stack_height_ft = float(get_col("stack_height (ft)", row))
        return stack_height_ft / self.ft_per_meter

    def stack_diameter_meter(self, row):
        stack_diameter_ft = float(get_col("stack_diameter (ft)", row))
        return stack_diameter_ft / self.ft_per_meter

    def gas_velocity_mps(self, row):
        gas_velocity_fts = float(get_col("exit_gas_velocity (ft/sec)", row))
        return gas_velocity_fts / self.ft_per_meter

    def gas_temperature_k(self, row):
        gas_temperature_f = float(get_col("exit_gas_temperature (f)", row))
        return self.fahrenheit_to_kelvin(gas_temperature_f)

    def fugitive_length_m(self, row):
        fugitive_length_f = float(get_col("fugitive_length_sigmax_ft", row))
        return fugitive_length_f / self.ft_per_meter

    def fugitive_width_m(self, row):
        fugitive_width_f = float(get_col("fugitive_width_sigmay_ft", row))
        return fugitive_width_f / self.ft_per_meter

    def release_height_m(self, row):
        try:
            release_height_ft = float(get_col("ICFAreaVolLineReleaseHeight", row))
            return release_height_ft / self.ft_per_meter
        except:
            return ""
