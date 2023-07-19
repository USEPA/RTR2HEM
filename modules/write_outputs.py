import os, shutil
import pandas as pd
from modules.utils import set_column, src_cat_name, timestamp

"""
If both category and wholesale selected then need to produce two sets of files for each template
"""


class WriteOuputs:
    templates_fp = "templates"

    def __init__(self, df):
        self.df = df
        self.create_folder()

    def create_folder(self):
        if not os.path.exists("outputs"):
            os.mkdir("outputs")
            
        self.out_fp = os.path.join("outputs", f"{src_cat_name}_{timestamp}")
        if not os.path.exists(self.out_fp):
            os.mkdir(self.out_fp)

    def write_to_template(self, template_name, sheetname, df, row):
        template_src = os.path.join(self.templates_fp, f"{template_name}.xlsx")
        output_dst = os.path.join(self.out_fp, f"{template_name}.xlsx")
        shutil.copyfile(template_src, output_dst)

        writer = pd.ExcelWriter(
            output_dst, engine="openpyxl", mode="a", if_sheet_exists="overlay"
        )
        df.to_excel(
            writer,
            sheet_name=sheetname,
            header=False,
            index=False,
            startcol=0,
            startrow=row,
        )
        writer.close()

    def emission_loc(self):
        sort_by = ["ICFFacilityID", "ICFSourceID"]
        emiss_loc_df = self.df
        emiss_loc_df = emiss_loc_df.sort_values(sort_by)

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

        for c in columns:
            if c not in self.df:
                emiss_loc_df[c] = ""

        emiss_loc_df = emiss_loc_df.drop_duplicates(columns)

        set_column(emiss_loc_df, "locationType", self.set_locationType)
        set_column(emiss_loc_df, "Longitude", self.set_Longitude)
        set_column(emiss_loc_df, "Latitude", self.set_Latitude)
        set_column(emiss_loc_df, "Lengthx", self.set_Lengthx)
        set_column(emiss_loc_df, "Lengthy", self.set_Lengthy)
        set_column(emiss_loc_df, "HorzDim", self.set_HorzDim)
        set_column(emiss_loc_df, "VertDim", self.set_VertDim)
        set_column(emiss_loc_df, "X2", self.set_X2)
        set_column(emiss_loc_df, "Y2", self.set_Y2)

        # set up category only
        cat_only_df = emiss_loc_df.loc[emiss_loc_df["ICFCatLevelModeling"] == "Yes"]

        # drop unneeded columns
        emiss_loc_df = emiss_loc_df[columns]
        cat_only_df = cat_only_df[columns]

        self.write_to_template(
            "HEM4_Emiss_Loc_ICF", "Emissions_Location", cat_only_df, 2
        )

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
