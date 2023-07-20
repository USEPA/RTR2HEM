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
    ]

    def __init__(self, df):
        self.df = df

    def create(self):
        emiss_loc_df = self.df.copy()
        emiss_loc_df = emiss_loc_df.sort_values(self.sort_by)

        for c in self.columns:
            if c not in self.df:
                emiss_loc_df[c] = ""

        emiss_loc_df = emiss_loc_df.drop_duplicates(self.columns)

        set_column(emiss_loc_df, "locationType", self.set_locationType)
        set_column(emiss_loc_df, "Longitude", self.set_Longitude)
        set_column(emiss_loc_df, "Latitude", self.set_Latitude)
        set_column(emiss_loc_df, "Lengthx", self.set_Lengthx)
        set_column(emiss_loc_df, "Lengthy", self.set_Lengthy)
        set_column(emiss_loc_df, "HorzDim", self.set_HorzDim)
        set_column(emiss_loc_df, "VertDim", self.set_VertDim)
        set_column(emiss_loc_df, "X2", self.set_X2)
        set_column(emiss_loc_df, "Y2", self.set_Y2)

        cat_emiss_loc_df = emiss_loc_df.loc[
            emiss_loc_df["ICFCatLevelModeling"] == "Yes"
        ]

        # drop unneeded columns
        emiss_loc_df = emiss_loc_df[self.columns]
        cat_emiss_loc_df = cat_emiss_loc_df[self.columns]

        return cat_emiss_loc_df, emiss_loc_df

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
