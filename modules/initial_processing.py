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
    def __init__(self, df, reg_codes=None):
        self.df = df
        self.reg_codes = reg_codes

    def set_column(self, column_name, func):
        self.df[column_name] = self.df.apply(lambda row: func(row), axis=1)

    def run(self):
        self.set_column("ICFFacilityID", self.set_icf_facility_id)
        self.set_column("ICFCatLevelModeling", self.is_selected_regulatory_code) # todo probably rename column


        return self.df

    def set_icf_facility_id(self, row):
        return row["state_county_fips"] + row["sppd_facility_identifier"]

    def is_selected_regulatory_code(self, row):
        if self.reg_codes == None:
            return True
        
        code = row["regulatory_code"]
        if code in self.reg_codes.keys():
            if self.reg_codes[code] == 1: 
                return True
        return False
            