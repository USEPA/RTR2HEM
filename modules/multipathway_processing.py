import pandas as pd

"""
TODO
- move overrides out
- split into
    - latitudes/longitudes
    - HH
    - Eco

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
        self.qryMP03ab_AppendLineLatLongs() # not implemented
        self.qryMP04aHH_CreateShellForChemSVs()
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
        columns = {
            "ICFFacilityID" : "Facility ID",
            "sppd_facility_identifier": "sppd_facility_identifier",
            "ICFSourceID": "Source ID",
            "y_coordinate" : "Latitude",
            "x_coordinate" : "Longitude",
            "ICFCatLevelModeling" : "ICFCatLevelModeling"
        }
        key_cols = list(columns.keys())

        # keep an eye out on cells that could be classified as NaN instead of ""
        tmp = self.df[key_cols].drop_duplicates()
        tmp = tmp.sort_values(key_cols)
        tmp = tmp.loc[
            (tmp["y_coordinate"] != "")
            & (tmp["x_coordinate"] != "")
            & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        del columns["ICFCatLevelModeling"]
        self.working_MPLatLongs = tmp[list(columns.keys())].rename(columns=columns)

    # working_MPLatLongsLine
    # TODO -- get working data for this
    def qryMP03aa_LineLatLons01(self):
        columns = {
            "ICFFacilityID": "Facility ID",
            "sppd_facility_identifier": "sppd_facility_identifier",
            "fugitive_2d_midpoint1_y_coordinate": "LineLatitude",
            "fugitive_2d_midpoint1_x_coordinate": "LineLongitude",
            "ICFCatLevelModeling": "ICFCatLevelModeling",
            "ICFSourceType": "ICFSourceType",
        }
        key_cols = list(columns.keys())

        tmp = self.df[key_cols].drop_duplicates()
        tmp = tmp.sort_values(key_cols)
        tmp = tmp.loc[
            (tmp["ICFSourceType"] == "N") & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        del columns["ICFCatLevelModeling"]
        del columns["ICFSourceType"]
        tmp = tmp[list(columns.keys())]

        self.working_MPLatLongsLine = tmp.rename(columns=columns)

    # working_MPLatLongsLine
    def qryMP03aa_LineLatLons02(self):
        columns = {
            "ICFFacilityID": "Facility ID",
            "sppd_facility_identifier": "sppd_facility_identifier",
            "fugitive_2d_midpoint2_y_coordinate": "LineLatitude",
            "fugitive_2d_midpoint2_x_coordinate": "LineLongitude",
            "ICFCatLevelModeling": "ICFCatLevelModeling",
            "ICFSourceType": "ICFSourceType",
        }
        key_cols = list(columns.keys())

        tmp = self.df[key_cols].drop_duplicates()
        tmp = tmp.sort_values(key_cols)
        tmp = tmp.loc[
            (tmp["ICFSourceType"] == "N") & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        del columns["ICFCatLevelModeling"]
        del columns["ICFSourceType"]
        tmp = tmp[list(columns.keys())]

        tmp = tmp.rename(columns=columns)
        self.working_MPLatLongsLine = pd.concat([self.working_MPLatLongsLine, tmp], ignore_index=True)

    # working_MPLatLongs
    # TODO -- get working data for this
    """
    Groups by facility id, sppd_facility_id, source id ... take the average of LineLatitude as latitude ... same with Longitude
    in these groups, then concat into working_MPLatLongs
    """
    def qryMP03ab_AppendLineLatLongs(self):
        columns = {
            "ICFFacilityID" : "Facility ID",
            "sppd_facility_identifier": "sppd_facility_identifier",
            "ICFSourceID": "Source ID",
            "y_coordinate" : "Latitude",
            "x_coordinate" : "Longitude"
        }
        key_cols = list(columns.keys())

    # working_MP04HH_T1ChemResults
    def qryMP04aHH_CreateShellForChemSVs(self):
        """
        SELECT "" AS [Src Cat], 
        qryMP03b_Avg_SourceLatLons_CatLevel.[Facility ID], 
        qryMP03b_Avg_SourceLatLons_CatLevel.[Avg Lat] AS Lat, 
        qryMP03b_Avg_SourceLatLons_CatLevel.[Avg Long] AS [Long], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.[ShortPB-HAP/EcoHAPName] AS [PB-HAP Grp], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.[Chem Name For Tier 2 Tool] AS Chem, 
        CDbl(0) AS [Emiss (TPY; chem)], static_MP_PBHAPChems_withHHEquivalencyFactors.TEF AS [TEF (chem)], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.EEF AS [EEF (chem)], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.REF AS [REF (chem)], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.[Date PB-HAP REF Created] AS [Date REF Created], 
        CDbl(0) AS [Emiss*REF (TPY; chem)], 
        static_MP_HHScreeningThresholds.[Tier 1 Screening Threshold (TPY)] AS [Scrn Thresh (TPY; grp)], 
        static_MP_HHScreeningThresholds.[Date Threshold Created] AS [Date Scrn Thresh Created], 
        CDbl(0) AS [SV (chem)] INTO working_MP04HH_T1ChemResults

        FROM qryMP03b_Avg_SourceLatLons_CatLevel, 
        static_MP_PBHAPChems_withHHEquivalencyFactors 
        INNER JOIN static_MP_HHScreeningThresholds 
        ON static_MP_PBHAPChems_withHHEquivalencyFactors.[ShortPB-HAP/EcoHAPName] = static_MP_HHScreeningThresholds.[ShortPB-HAPName]

        GROUP BY "", 
        qryMP03b_Avg_SourceLatLons_CatLevel.[Facility ID], 
        qryMP03b_Avg_SourceLatLons_CatLevel.[Avg Lat], 
        qryMP03b_Avg_SourceLatLons_CatLevel.[Avg Long], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.[ShortPB-HAP/EcoHAPName], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.[Chem Name For Tier 2 Tool], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.TEF, 
        static_MP_PBHAPChems_withHHEquivalencyFactors.EEF, 
        static_MP_PBHAPChems_withHHEquivalencyFactors.REF, 
        static_MP_PBHAPChems_withHHEquivalencyFactors.[Date PB-HAP REF Created], 
        static_MP_HHScreeningThresholds.[Tier 1 Screening Threshold (TPY)], 
        static_MP_HHScreeningThresholds.[Date Threshold Created], 
        CDbl(0)

        ORDER BY "", 
        qryMP03b_Avg_SourceLatLons_CatLevel.[Facility ID], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.[ShortPB-HAP/EcoHAPName], 
        static_MP_PBHAPChems_withHHEquivalencyFactors.[Chem Name For Tier 2 Tool];
        """
        pass
