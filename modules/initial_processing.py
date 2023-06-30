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
        self.set_column(
            "EMISSIONS_TPY", self.set_selected_emission_type
        )
        self.set_column("ICFEmissionProcessGroupAbbr", self.set_epg_abbreviations)
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