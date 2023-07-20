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
    ]

    def __init__(self, df):
        self.df = df

    def create(self):
        fac_address_df = self.df
        fac_address_df = fac_address_df.sort_values(self.sort_by)
        fac_address_df = fac_address_df.drop_duplicates(self.columns)

        cat_fac_address_df = fac_address_df.loc[
            fac_address_df["ICFCatLevelModeling"] == "Yes"
        ]

        fac_address_df = fac_address_df[self.columns]
        cat_fac_address_df = cat_fac_address_df[self.columns]

        return cat_fac_address_df, fac_address_df
