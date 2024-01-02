class FacilityAddress:
    sort_by = ["ICFFacilityID", "facility_name"]

    columns = [
        "ICFFacilityID",
        "facility_name",
        "location_address",
        "city",
        "state_abbr",
        "zipcode",
        "county_name",
        "ICFCatLevelModeling",
    ]

    filename = "FacAddress"
    template_name = "HEM4_Fac_Address_ICF"
    sheet_name = "Facility_Address"
    rowstart = 1
    colstart = 0

    def __init__(self, df):
        self.df = df

    def create(self):
        fac_address_df = self.df.copy()
        fac_address_df = fac_address_df.sort_values(self.sort_by)

        # Category only
        cat_fac_address_df = fac_address_df.drop_duplicates(self.columns)
        cat_fac_address_df = cat_fac_address_df.loc[
            cat_fac_address_df["ICFCatLevelModeling"] == "Yes"
        ]

        self.columns.pop()  # remove ICFCatLevelModeling
        self.cat_df = cat_fac_address_df[self.columns]

        # Wholesale
        fac_address_df = fac_address_df.drop_duplicates(self.columns)
        self.whole_df = fac_address_df[self.columns]

        return self
