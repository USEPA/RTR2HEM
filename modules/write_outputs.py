import os, shutil
import pandas as pd
from modules.outputs_writer.emiss_loc import EmissionLoc
from modules.outputs_writer.fac_address import FacilityAddress
from modules.utils import src_cat_name, timestamp

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

    def run(self):
        cat_emis_loc, whole_emis_loc = EmissionLoc(self.df).create()
        self.write_to_template(
            "HEM4_Emiss_Loc_ICF", "Emissions_Location", cat_emis_loc, 2
        )

        cat_fac_address, whole_fac_address = FacilityAddress(self.df).create()
        self.write_to_template(
            "HEM4_Fac_Address_ICF", "Facility_Address", cat_fac_address, 1
        )

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


"""

"""
