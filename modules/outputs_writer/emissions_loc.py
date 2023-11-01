from modules.utils import set_column


class EmissionLoc:
    sort_by = ["ICFFacilityID", "ICFSourceID"]

    columns = [
        "ICFFacilityID",
        "ICFSourceID",
        "locationType",
        "Longitude",
        "Latitude",
        "UTMzone",
        "ICFSourceType",
        "Lengthx",
        "Lengthy",
        "fugitive_angle_degrees",
        "HorzDim",
        "VertDim",
        "ICFAreaVolLineReleaseHeight_m",
        "ICFStackHeight_m",
        "ICFStackDiameter_m",
        "ICFExitGasVelocity_mps",
        "ICFExitGasTemperature_K",
        "Elevation_m",
        "X2",
        "Y2",
        "ICFCatLevelModeling",
    ]

    filename = "EmisLoc"
    template_name = "HEM4_Emiss_Loc_ICF"
    sheet_name = "Emissions_Location"
    rowstart = 2
    colstart = 0

    def __init__(self, df):
        self.df = df

    def create(self):
        emiss_loc_df = self.df.copy()

        for c in self.columns:
            if c not in self.df:
                emiss_loc_df[c] = ""

        set_column(emiss_loc_df, "locationType", self.set_locationType)
        set_column(emiss_loc_df, "Longitude", self.set_Longitude)
        set_column(emiss_loc_df, "Latitude", self.set_Latitude)
        set_column(emiss_loc_df, "Lengthx", self.set_Lengthx)
        set_column(emiss_loc_df, "Lengthy", self.set_Lengthy)
        set_column(emiss_loc_df, "HorzDim", self.set_HorzDim)
        set_column(emiss_loc_df, "VertDim", self.set_VertDim)
        set_column(emiss_loc_df, "X2", self.set_X2)
        set_column(emiss_loc_df, "Y2", self.set_Y2)

        emiss_loc_df = emiss_loc_df.drop_duplicates(self.columns)  # groupby

        cat_emiss_loc_df = emiss_loc_df.loc[
            emiss_loc_df["ICFCatLevelModeling"] == "Yes"
        ]

        # drop unneeded columns
        self.columns.pop()  # remove ICFCatLevelModeling
        self.whole_df = emiss_loc_df[self.columns].sort_values(self.sort_by)
        self.cat_df = cat_emiss_loc_df[self.columns].sort_values(self.sort_by)

        return self

    def set_locationType(self, row):
        return "L"

    def set_Longitude(self, row):
        erp_value = row["emission_release_point_type"]
        if erp_value == "9":
            return row["fugitive_2d_midpoint1_x_coordinate"]
        return row["x_coordinate"]

    def set_Latitude(self, row):
        erp_value = row["emission_release_point_type"]
        if erp_value == "9":
            return row["fugitive_2d_midpoint1_y_coordinate"]
        return row["y_coordinate"]

    """
    "SELECT DISTINCT working_CrosswalkEmissionInventory.ICFFacilityID AS FacilityID, 
    working_CrosswalkEmissionInventory.ICFSourceID AS SourceID, 
    'L' AS LocationType, 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',working_CrosswalkEmissionInventory.FUGITIVE_2D_MIDPOINT1_X_COORDINATE, working_CrosswalkEmissionInventory.X_COORDINATE) AS Longitude, 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',working_CrosswalkEmissionInventory.FUGITIVE_2D_MIDPOINT1_Y_COORDINATE, working_CrosswalkEmissionInventory.Y_COORDINATE) AS Latitude, 
    working_CrosswalkEmissionInventory.blank AS UTMzone, working_CrosswalkEmissionInventory.ICFSourceType AS SourceType, " _

    & "IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',[working_CrosswalkEmissionInventory]![ICFFugitiveWidth_m],[working_CrosswalkEmissionInventory]![ICFFugitiveLength_m]) AS Lengthx, 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9' OR [working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='10',Null,[working_CrosswalkEmissionInventory]![ICFFugitiveWidth_m]) AS Lengthy, " _

    & "working_CrosswalkEmissionInventory.FUGITIVE_ANGLE_DEGREES AS Angle, 
    IIf([ICFSourceType]<>'V',Null,[ICFFugitiveWidth_m]/4.3) AS HorzDim, 
    IIf([ICFSourceType]<>'V',Null,[ICFAreaVolLineReleaseHeight_m]*2/2.15) AS VertDim, 
    working_CrosswalkEmissionInventory.ICFAreaVolLineReleaseHeight_m AS AreaVolReleaseHgt, 
    working_CrosswalkEmissionInventory.ICFStackHeight_m AS StackHgt_m, 
    working_CrosswalkEmissionInventory.ICFStackDiameter_m AS StackDiameter_m, " _

    & "working_CrosswalkEmissionInventory.ICFExitGasVelocity_mps AS ExitGasVel_m, 
    working_CrosswalkEmissionInventory.ICFExitGasTemperature_K AS ExitGasTemp_K, 
    working_CrosswalkEmissionInventory.blank AS Elevation_m, 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',working_CrosswalkEmissionInventory.FUGITIVE_2D_MIDPOINT2_X_COORDINATE, Null) AS X2, 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',working_CrosswalkEmissionInventory.FUGITIVE_2D_MIDPOINT2_Y_COORDINATE, Null) AS Y2 " _

    & "INTO output_EmissionLocation " _
    & "FROM working_CrosswalkEmissionInventory " _

    
    & "GROUP BY working_CrosswalkEmissionInventory.ICFFacilityID, 
    working_CrosswalkEmissionInventory.ICFSourceID, 
    'L', 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',working_CrosswalkEmissionInventory.FUGITIVE_2D_MIDPOINT1_X_COORDINATE, working_CrosswalkEmissionInventory.X_COORDINATE), 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',working_CrosswalkEmissionInventory.FUGITIVE_2D_MIDPOINT1_Y_COORDINATE, working_CrosswalkEmissionInventory.Y_COORDINATE), 
    working_CrosswalkEmissionInventory.ICFSourceType, 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',[working_CrosswalkEmissionInventory]![ICFFugitiveWidth_m], [working_CrosswalkEmissionInventory]![ICFFugitiveLength_m]), 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9' 

    OR [working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='10',Null,[working_CrosswalkEmissionInventory]![ICFFugitiveWidth_m]), 
    working_CrosswalkEmissionInventory.FUGITIVE_ANGLE_DEGREES, IIf([ICFSourceType]<>'V',Null,[ICFFugitiveWidth_m]/4.3), " _

    & "IIf([ICFSourceType]<>'V',Null,[ICFAreaVolLineReleaseHeight_m]*2/2.15), 
    working_CrosswalkEmissionInventory.ICFAreaVolLineReleaseHeight_m, 
    working_CrosswalkEmissionInventory.ICFStackHeight_m, 
    working_CrosswalkEmissionInventory.ICFStackDiameter_m, 
    working_CrosswalkEmissionInventory.ICFExitGasVelocity_mps, 
    working_CrosswalkEmissionInventory.ICFExitGasTemperature_K, 
    working_CrosswalkEmissionInventory.blank, 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',working_CrosswalkEmissionInventory.FUGITIVE_2D_MIDPOINT2_X_COORDINATE, Null), 
    IIf([working_CrosswalkEmissionInventory]![EMISSION_RELEASE_POINT_TYPE]='9',working_CrosswalkEmissionInventory.FUGITIVE_2D_MIDPOINT2_Y_COORDINATE, Null), " _
    & "working_CrosswalkEmissionInventory.ICFFugitiveLength_m, 
    working_CrosswalkEmissionInventory.ICFFugitiveWidth_m, 
    working_CrosswalkEmissionInventory.ICFCatLevelModeling, 
    working_CrosswalkEmissionInventory.StateGroup " _

    & "HAVING (((working_CrosswalkEmissionInventory.ICFCatLevelModeling)='YES') 
    AND ((working_CrosswalkEmissionInventory.StateGroup)=" & intJ & ")) " _

    & "ORDER BY working_CrosswalkEmissionInventory.ICFFacilityID, 
    working_CrosswalkEmissionInventory.ICFSourceID;"
    """

    def set_Lengthx(self, row):
        erp_value = row["emission_release_point_type"]
        if erp_value == "9":
            return row["ICFFugitiveWidth_m"]
        return row["ICFFugitiveLength_m"]

    def set_Lengthy(self, row):
        erp_value = row["emission_release_point_type"]
        if erp_value == "9" or erp_value == "10":
            return ""
        return row["ICFFugitiveWidth_m"]

    def set_HorzDim(self, row):
        src_type = row["ICFSourceType"]
        if src_type == "V":
            return float(row["ICFFugitiveWidth_m"]) / 4.3
        return ""

    def set_VertDim(self, row):
        src_type = row["ICFSourceType"]
        if src_type == "V":
            return float(row["ICFAreaVolLineReleaseHeight_m"]) * 2 / 2.15
        return ""

    def set_X2(self, row):
        erp_value = row["emission_release_point_type"]
        if erp_value == "9":
            return row["fugitive_2d_midpoint2_x_coordinate"]
        return ""

    def set_Y2(self, row):
        erp_value = row["emission_release_point_type"]
        if erp_value == "9":
            return row["fugitive_2d_midpoint2_y_coordinate"]
        return ""
