import os, shutil
import pandas as pd
from modules.outputs_writer.emissions_loc import EmissionLoc
from modules.outputs_writer.fac_address import FacilityAddress
from modules.outputs_writer.fac_list import FacilityList
from modules.outputs_writer.hap_emissions import HapEmissions
from modules.utils import src_cat_name, timestamp, only_category

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
        emis_loc = EmissionLoc(self.df).create()
        self.write_to_template(emis_loc)

        fac_address = FacilityAddress(self.df).create()
        self.write_to_template(fac_address)

        fac_list = FacilityList(self.df).create()
        self.write_to_template(fac_list)

        hap_emissions = HapEmissions(self.df).create()
        self.write_to_template(hap_emissions)

    def write_to_template(self, result):
        template_name = result.template_name
        sheetname = result.sheet_name
        row = result.rowstart

        # Write category records
        filename = "cat"

        template_src = os.path.join(self.templates_fp, f"{template_name}.xlsx")
        output_dst = os.path.join(self.out_fp, f"{template_name}_{filename}.xlsx")
        shutil.copyfile(template_src, output_dst)

        writer = pd.ExcelWriter(
            output_dst, engine="openpyxl", mode="a", if_sheet_exists="overlay"
        )
        result.cat_df.to_excel(
            writer,
            sheet_name=sheetname,
            header=False,
            index=False,
            startcol=0,
            startrow=row,
        )
        writer.close()

        # Write wholesale records
        if not only_category:
            filename = "whole"

            template_src = os.path.join(self.templates_fp, f"{template_name}.xlsx")
            output_dst = os.path.join(self.out_fp, f"{template_name}_{filename}.xlsx")
            shutil.copyfile(template_src, output_dst)

            writer = pd.ExcelWriter(
                output_dst, engine="openpyxl", mode="a", if_sheet_exists="overlay"
            )
            result.whole_df.to_excel(
                writer,
                sheet_name=sheetname,
                header=False,
                index=False,
                startcol=0,
                startrow=row,
            )
            writer.close()
