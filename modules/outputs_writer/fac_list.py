class FacilityList:
    sort_by = ["ICFFacilityID"]

    columns = ["ICFFacilityID"]

    def __init__(self, df):
        self.df = df

    def create(self):
        fac_list_df = self.df.copy()
        fac_list_df = fac_list_df.sort_values(self.sort_by)
        fac_list_df = fac_list_df.drop_duplicates(self.columns)

        cat_fac_list_df = fac_list_df.loc[fac_list_df["ICFCatLevelModeling"] == "Yes"]

        fac_list_df = fac_list_df[self.columns]
        cat_fac_list_df = cat_fac_list_df[self.columns]

        return cat_fac_list_df, fac_list_df
