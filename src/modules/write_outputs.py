import os, shutil
import pandas as pd
from src.modules.output_data import (
    EmissionLoc,
    FacilityAddress,
    FacilityList,
    HapEmissions,
)
from src.accdb_manager import AccdbManager
from src.utils import config


class WriteOutputs:
    templates_fp = "templates"

    def __init__(self):
        self.base = config.output_dir
        if os.getcwd() == config.output_dir:
            self.base = os.path.join(config.output_dir, "outputs")
        self.runname = f"{config.src_cat_name}_{config.emission_type}"

        self.output_dir = os.path.join(
            self.base, f"{self.runname}_HEMInputsAndXWalks_{config.timestamp}"
        )
        self.create_folder()

        accdb_fp = os.path.join(
            self.output_dir, f"{self.runname}_XWalks_{config.timestamp}.accdb"
        )
        self.accdb = AccdbManager(accdb_fp)

    def create_folder(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

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
        # Write category records
        filename = f"{self.runname}_{result.filename}_Cat_{config.timestamp}"
        out_dst = self.copy_template(filename, result)
        self.write_excel_sheet(out_dst, result.cat_df, result)

        # Write whole records only if actual emissions
        if not config.only_category and config.emission_type == "Actual":
            filename = f"{self.runname}_{result.filename}_Whole_{config.timestamp}"
            out_dst = self.copy_template(filename, result)
            self.write_excel_sheet(out_dst, result.whole_df, result)

    def copy_template(self, name, result):
        template_src = os.path.join(self.templates_fp, f"{result.template_name}.xlsx")
        out_dst = os.path.join(self.output_dir, f"{name}.xlsx")
        shutil.copyfile(template_src, out_dst)
        return out_dst

    def write_excel_sheet(self, fp, df, data):
        writer = pd.ExcelWriter(
            fp, engine="openpyxl", mode="a", if_sheet_exists="overlay"
        )
        df.to_excel(
            writer,
            sheet_name=data.sheet_name,
            header=False,
            index=False,
            startrow=data.rowstart,
            startcol=data.colstart,
        )
        writer.close()
