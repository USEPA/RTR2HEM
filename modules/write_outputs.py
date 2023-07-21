import os, shutil
import pandas as pd
from openpyxl import load_workbook
from modules.outputs_writer.emissions_loc import EmissionLoc
from modules.outputs_writer.fac_address import FacilityAddress
from modules.outputs_writer.fac_list import FacilityList
from modules.outputs_writer.hap_emissions import HapEmissions
from modules.outputs_writer.write_accdb import AccdbWriter
from modules.utils import src_cat_name, timestamp, emission_type, only_category


class WriteOuputs:
    templates_fp = "templates"
    filename_base = f"{src_cat_name}{timestamp}_{emission_type.split(' ')[0]}"

    def __init__(self):
        self.out_fp = os.path.join(
            "outputs", f"{self.filename_base}_HEMInputsAndXWalks"
        )
        self.create_folder()

        accdb_fp = os.path.join(self.out_fp, f"{self.filename_base}_XWalks.accdb")
        self.accdb = AccdbWriter(accdb_fp)

    def create_folder(self):
        if not os.path.exists("outputs"):
            os.mkdir("outputs")
        if os.path.exists(self.out_fp):
            shutil.rmtree(self.out_fp)
        os.mkdir(self.out_fp)

    def run(self, df):
        self.df = df
        emis_loc = EmissionLoc(self.df).create()
        self.write_to_template(emis_loc)

        fac_address = FacilityAddress(self.df).create()
        self.write_to_template(fac_address)

        fac_list = FacilityList(self.df).create()
        self.write_to_template(fac_list)

        hap_emissions = HapEmissions(self.df).create()
        self.write_to_template(hap_emissions)

    def write_to_template(self, result):
        template_src = os.path.join(self.templates_fp, f"{result.template_name}.xlsx")
        filename = f"{self.filename_base}_{result.filename}_Cat"
        out_dst = os.path.join(self.out_fp, f"{filename}.xlsx")

        # Write category records
        shutil.copyfile(template_src, out_dst)
        self.write_excel_sheet(
            out_dst, result.cat_df, result.sheet_name, result.rowstart
        )

        # Write whole records
        if not only_category:
            filename = f"{self.filename_base}_{result.filename}_Whole"
            out_dst = os.path.join(self.out_fp, f"{filename}.xlsx")
            shutil.copyfile(template_src, out_dst)
            self.write_excel_sheet(
                out_dst, result.whole_df, result.sheet_name, result.rowstart
            )

    def write_excel_sheet(self, fp, df, sheet, row):
        writer = pd.ExcelWriter(
            fp, engine="openpyxl", mode="a", if_sheet_exists="overlay"
        )
        df.to_excel(
            writer,
            sheet_name=sheet,
            header=False,
            index=False,
            startrow=row,
        )
        writer.close()

    def insert_notes(self, src_fp, dst_fp):
        template_wb = load_workbook(src_fp)
        template_ws = template_wb.active

        out_wb = load_workbook(dst_fp)
        out_ws = out_wb.active

        for i, row in enumerate(template_ws):
            if i > 2:
                break
            for cell in row:
                if cell.comment:
                    out_ws[cell.coordinate].comment = cell.comment

        out_wb.save(dst_fp)
        out_wb.close()
        template_wb.close()
