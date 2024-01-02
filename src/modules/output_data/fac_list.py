class FacilityList:
    sort_by = ["ICFFacilityID"]

    columns = ["ICFFacilityID", "ICFCatLevelModeling"]

    filename = "FacList"
    template_name = "HEM4_Facility_List_Options_ICF"
    sheet_name = "Facility List Options"
    rowstart = 2
    colstart = 0

    def __init__(self, df):
        self.df = df

    def create(self):
        fac_list_df = self.df.copy()
        fac_list_df = fac_list_df.sort_values(self.sort_by)

        # Category only
        cat_fac_list_df = fac_list_df.drop_duplicates(self.columns)
        cat_fac_list_df = cat_fac_list_df.loc[
            cat_fac_list_df["ICFCatLevelModeling"] == "Yes"
        ]

        self.columns.pop()  # remove ICFCatLevelModeling
        self.cat_df = cat_fac_list_df[self.columns]

        # Wholesale
        fac_list_df = fac_list_df.drop_duplicates(self.columns)
        self.whole_df = fac_list_df[self.columns]

        return self
