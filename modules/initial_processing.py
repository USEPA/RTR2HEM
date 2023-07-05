import pandas as pd
from .utils import emission_type, static_xls

"""
Next steps:
''ADD SOME NEW FIELDS TO THE EMISSION INVENTORY, IDENTIFY THE DESIRED EMISSIONS FIELD,
''POPULATE EPGROUP ABBREVIATIONS, CONVERT TO METRIC, IDENTIFY AERMOD SOURCE TYPES,
''CREATE STATE GROUPS AS NEEDED FOR FILE SIZE CONSTRAINTS -
''CREATE CROSSWALK FILE

uses:
    table "input_EmissionInventory_withICFWork"
"""

"""
Would it be possible to get an example input that actually uses this? 
Everything in refractories is "P" so this will be a little tough to 100% test


''WANT TO LEAVE CERTAIN FIELDS AS NULL IF THEY DO NOT APPLY TO THAT PARTICULAR SOURCE TYPE:
''SOURCES THAT ARE NOT AREA, LINE, OR VOLUME DO NOT RECEIVE FUGITIVERELEASEHEIGHT,
''SOURCES THAT ARE NOT POINTS DO NOT RECEIVE STACK HEIGHTS, TEMPERATURES, DIAMETERS, OR VELOCITIES,
''SOURCES THAT ARE NOT AREA DO NOT RECEIVE FUGITIVE LENGTHS,
''SOURCES THAT ARE NOT AREA, LINE, OR VOLUME DO NOT RECEIVE FUGITIVE WIDTHS,
''SOURCES THAT ARE NOT AREA DO NOT RECEIVE FUGITIVE ANGLES.

"SELECT input_EmissionInventory_withICFWork.StateGroup, 
        input_EmissionInventory_withICFWork.ICFFacilityID, 
        input_EmissionInventory_withICFWork.SPPD_FACILITY_IDENTIFIER, 
        input_EmissionInventory_withICFWork.ICFSourceID, 
        input_EmissionInventory_withICFWork.ICFSourceType, 
        input_EmissionInventory_withICFWork.POLLUTANT_CODE, 
        input_EmissionInventory_withICFWork.POLLUTANT_DESCRIPTION,
        input_EmissionInventory_withICFWork.HAP_CATEGORY_NAME, 

        input_EmissionInventory_withICFWork.EMISSIONS_TPY, 
        ([Emissions_TPY]*[Metal_Speciation_Factor]) AS ICFModelEmissionTPY, '' AS blank, " _
        
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

        ------------ACTUAL LOGIC STARTS HERE------------

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

        & "'' AS blank3, static_PollutantCrosswalk_andMetalSpeciations.Metal_Speciation_Factor AS ICFMetal_Speciation_Factor, " _
        & "'' AS blank4, input_EmissionInventory_withICFWork.FACILITY_NAME, input_EmissionInventory_withICFWork.LOCATION_ADDRESS, input_EmissionInventory_withICFWork.CITY, " _
        & "input_EmissionInventory_withICFWork.COUNTY_NAME, input_EmissionInventory_withICFWork.STATE_ABBR, input_EmissionInventory_withICFWork.ZIPCODE " _
        & "INTO working_CrosswalkEmissionInventory " _
        
        & "FROM input_EmissionInventory_withICFWork INNER JOIN 
        static_PollutantCrosswalk_andMetalSpeciations ON 
        input_EmissionInventory_withICFWork.POLLUTANT_CODE=static_PollutantCrosswalk_andMetalSpeciations.Pollutant_Code;"
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
        static_pollutantCrosswalk = pd.read_excel(static_xls, "static_PollutantCrosswalk_andMe")
        static_pollutantCrosswalk.columns = static_pollutantCrosswalk.columns.str.lower()
        self.df = pd.merge(self.df, static_pollutantCrosswalk, on="pollutant_code", how="inner", suffixes=('', '_y'))
        # drop duplicate columns
        self.df.drop(self.df.filter(regex='_y$').columns, axis=1, inplace=True)

    def run(self):
        self.set_column("ICFFacilityID", self.set_icf_facility_id)
        self.set_column("ICFCatLevelModeling", self.is_selected_regulatory_code)
        self.set_column("EMISSIONS_TPY", self.set_selected_emission_type)
        self.set_column("ICFEmissionProcessGroupAbbr", self.set_epg_abbreviations)
        self.set_column("ICFSourceType", self.set_source_type)
        self.set_column("ICFAreaVolLineReleaseHeight", self.set_release_height)

        # unit conversions
        # might not need to store
        self.set_column("ICFStackHeight_m", self.stack_height_meter)
        self.set_column("ICFStackDiameter_m", self.stack_diameter_meter)
        self.set_column("ICFExitGasVelocity_mps", self.gas_velocity_mps)
        self.set_column("ICFExitGasTemperature_K", self.gas_temperature_k)
        self.set_column("ICFFugitiveLength_m", self.fugitive_length_m)
        self.set_column("ICFFugitiveWidth_m", self.fugitive_width_m)
        self.set_column("ICFAreaVolLineReleaseHeight_m", self.release_height_m)

        self.join_static_PollutantCrosswalk_andMetalSpeciations()

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
        gas_velocity_fts = float(row["exit_gas_velocity (ft/sec)"])
        return gas_velocity_fts / self.ft_per_meter

    def gas_temperature_k(self, row):
        gas_temperature_f = float(row["exit_gas_temperature (f)"])
        return self.fahrenheit_to_kelvin(gas_temperature_f)

    def fugitive_length_m(self, row):
        fugitive_length_f = float(row["fugitive_length_sigmax_ft"])
        return fugitive_length_f / self.ft_per_meter

    def fugitive_width_m(self, row):
        fugitive_width_f = float(row["fugitive_width_sigmay_ft"])
        return fugitive_width_f / self.ft_per_meter

    def release_height_m(self, row):
        try:
            release_height_ft = float(row["ICFAreaVolLineReleaseHeight"])
            return release_height_ft / self.ft_per_meter
        except:
            return ""
