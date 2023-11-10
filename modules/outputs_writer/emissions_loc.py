from modules.utils import vset_column


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

        # fmt: off
        emiss_loc_df["locationType"] = "L"
        vset_column(emiss_loc_df, "Longitude", self.set_Longitude, ["emission_release_point_type", "fugitive_2d_midpoint1_x_coordinate", "x_coordinate"])
        vset_column(emiss_loc_df, "Latitude", self.set_Latitude, ["emission_release_point_type", "fugitive_2d_midpoint1_y_coordinate", "y_coordinate"])
        vset_column(emiss_loc_df, "Lengthx", self.set_Lengthx, ["emission_release_point_type", "ICFFugitiveWidth_m", "ICFFugitiveLength_m"])
        vset_column(emiss_loc_df, "Lengthy", self.set_Lengthy, ["emission_release_point_type", "ICFFugitiveWidth_m"])
        vset_column(emiss_loc_df, "HorzDim", self.set_HorzDim, ["ICFSourceType", "ICFFugitiveWidth_m"])
        vset_column(emiss_loc_df, "VertDim", self.set_VertDim, ["ICFSourceType", "ICFAreaVolLineReleaseHeight_m"])
        vset_column(emiss_loc_df, "X2", self.set_X2, ["emission_release_point_type", "fugitive_2d_midpoint2_x_coordinate"])
        vset_column(emiss_loc_df, "Y2", self.set_Y2, ["emission_release_point_type", "fugitive_2d_midpoint2_y_coordinate"])
        # fmt: on

        emiss_loc_df = emiss_loc_df.drop_duplicates(self.columns)  # groupby

        cat_emiss_loc_df = emiss_loc_df.loc[
            emiss_loc_df["ICFCatLevelModeling"] == "Yes"
        ]

        # drop unneeded columns
        self.columns.pop()  # remove ICFCatLevelModeling
        self.whole_df = emiss_loc_df[self.columns].sort_values(self.sort_by)
        self.cat_df = cat_emiss_loc_df[self.columns].sort_values(self.sort_by)
        return self

    def set_Longitude(self, erp_value, fug1_x, x):
        if erp_value == "9":
            return fug1_x
        return x

    def set_Latitude(self, erp_value, fug1_y, y):
        if erp_value == "9":
            return fug1_y
        return y

    def set_Lengthx(self, erp_value, fug_width, fug_length):
        if erp_value == "9":
            return fug_width
        return fug_length

    def set_Lengthy(self, erp_value, fug_width):
        if erp_value == "7" or erp_value == "9":
            return ""
        return fug_width

    def set_HorzDim(self, src_type, fug_width):
        if src_type == "V":
            return float(fug_width) / 4.3
        return ""

    def set_VertDim(self, src_type, release_height):
        if src_type == "V":
            return float(release_height) * 2 / 2.15
        return ""

    def set_X2(self, erp_value, fug2_x):
        if erp_value == "9":
            return fug2_x
        return ""

    def set_Y2(self, erp_value, fug2_y):
        if erp_value == "9":
            return fug2_y
        return ""
