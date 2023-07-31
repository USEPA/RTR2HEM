"""
This occurs across a series of Access queries. 
These queries must use only the sources inside the source category, 
and they must use the emissions after any speciations were applied 
in the basic processing noted above.

ONLY run this on actual/allowable emissions, NOT acute

For each query: in the side menu right click > design view > right click the tab at the top select "sql view"
"data sheet" view will show you what the resulting df should look like
"""


class MultiPathwayProcessing:
    def __init__(self, df):
        self.df = df

    def run(self):
        self.qryMP00aEco_DuplicateCrosswalkInventory()
        self.qryMP00bEco_AddDivalentMercury()
        self.qryMP03a_SourceLatLons_CatLevel()
        self.qryMP03aa_LineLatLons01()
        self.qryMP03aa_LineLatLons02()
        return self.df

    # working_CrosswalkEmissionInventory_Eco
    def qryMP00aEco_DuplicateCrosswalkInventory(self):
        self.working_CrosswalkEmissionInventory_Eco = self.df.copy()

    # working_CrosswalkEmissionInventory_Eco
    def qryMP00bEco_AddDivalentMercury(self):
        tmp = self.working_CrosswalkEmissionInventory_Eco
        tmp = tmp.loc[
            tmp["chem name for tier 2 tool"] == "Methyl Mercury (Emitted as Divalent)"
        ]
        self.working_CrosswalkEmissionInventory_Eco = tmp

    # working_MPLatLongs
    def qryMP03a_SourceLatLons_CatLevel(self):
        columns = [
            "ICFFacilityID", # Facility ID
            "sppd_facility_identifier",
            "ICFSourceID", # Source ID
            "y_coordinate", # Latitude
            "x_coordinate", # Longitude
            "ICFCatLevelModeling",
        ]

        # keep an eye out on cells that could be classified as NaN instead of ""
        tmp = self.df[columns].drop_duplicates()
        tmp = tmp.sort_values(columns)
        tmp = tmp.loc[
            (tmp["y_coordinate"] != "")
            & (tmp["x_coordinate"] != "")
            & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        columns.pop()  # drop ICFCatLevelModeling
        self.working_MPLatLongs = tmp[columns]

    # working_MPLatLongsLine
    def qryMP03aa_LineLatLons01(self):
        columns = [
            "ICFFacilityID", # Facility ID
            "sppd_facility_identifier",
            "ICFSourceID", # Source ID
            "fugitive_2d_midpoint1_y_coordinate", # LineLatitude
            "fugitive_2d_midpoint1_x_coordinate", # LineLongitude
            "ICFCatLevelModeling",
            "ICFSourceType"
        ]

        tmp = self.df[columns].drop_duplicates()
        tmp = tmp.sort_values(columns)
        tmp = tmp.loc[
            (tmp["ICFSourceType"] == "N")
            & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        # drop ICFCatLevelModeling, ICFSourceType
        columns = columns[:-2]
        self.working_MPLatLongsLine = tmp[columns]

    # working_MPLatLongsLine
    # TODO -- get working data for this
    def qryMP03aa_LineLatLons02(self):
        columns = [
            "ICFFacilityID", # Facility ID
            "sppd_facility_identifier",
            "ICFSourceID", # Source ID
            "fugitive_2d_midpoint2_y_coordinate", # LineLatitude
            "fugitive_2d_midpoint2_x_coordinate", # LineLongitude
            "ICFCatLevelModeling",
            "ICFSourceType"
        ]

        tmp = self.df[columns].drop_duplicates()
        tmp = tmp.sort_values(columns)
        tmp = tmp.loc[
            (tmp["ICFSourceType"] == "N")
            & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        # drop ICFCatLevelModeling, ICFSourceType
        columns = columns[:-2]
        # self.working_MPLatLongsLine = tmp[columns]
