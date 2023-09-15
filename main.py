import os, shutil
import logging
import numpy as np
import pandas as pd

from modules.initial_processing import InitialProcessing
from modules.source_ids import SourceIDs
from modules.multipathway_processing import MultiPathwayProcessing
from modules.write_outputs import WriteOutputs
from modules.utils import get_static, config

from modules.GUI import SettingsGUI, ColumnMapGUI, EpgGUI, RegCodesGUI


class RTR2HEM:
    def __init__(self):
        self.settings_select()
        self.epgs_select()
        self.reg_codes_and_initial_processing()
        self.source_ids_create()
        self.multipathway_processing()
        self.write_all_remaining_outputs()

    def settings_select(self):
        """1-7a"""
        logging.info("Settings select")

        settings = SettingsGUI()
        # loaded from interface
        if settings.option_var.get() == "0":
            ColumnMapGUI()

        config.out = WriteOutputs()
        config.rename_columns()
        config.set_input_df_column_types()

        # minimize wait by writing static files during GUI process
        config.out.accdb.write(
            "00 - RTR-HEM and PBHAP Poll Xwalk",
            get_static("static_PollutantCrosswalk_andMetalSpeciations"),
        )
        config.out.accdb.write(
            "00 - Tier 1 Eco Mpath EcoEEFs",
            get_static("static_MP_EcoEquivalencyFactors"),
        )
        config.out.accdb.write(
            "00 - Tier 1 Eco Mpath Thresh",
            get_static("static_MP_EcoScreeningThresholds"),
        )
        config.out.accdb.write(
            "00 - Tier 1 HumHealth Mpath REFs",
            get_static("static_MP_PBHAPChems_withHHEquivalencyFactors"),
        )
        config.out.accdb.write(
            "00 - Tier 1 HumHealth Mpath Thresh",
            get_static("static_MP_HHScreeningThresholds"),
        )

    def epgs_select(self):
        """7b"""
        logging.info("EPGs select")

        epgs = config.input_df["emission_process_group"]
        epgs = epgs.replace("", np.nan).dropna().unique().tolist()
        epgs.sort()
        epgs = dict(zip(epgs, [""] * len(epgs)))

        # populate with import
        if config.epg_import is not None:
            epg_import = config.epg_import.to_dict("records")
            for i, item in enumerate(epg_import):
                key = item["emission_process_group"]
                val = item["icfemissionprocessgroupabbr"]
                if key in epgs.keys():
                    epgs[key] = val

        if epgs:
            epgs = EpgGUI(epgs).get_response()

        self.epgs = epgs
        self.epg_pairs = {
            config.epg_required[0]: list(epgs.keys()),
            config.epg_required[1]: list(epgs.values()),
        }

    def reg_codes_and_initial_processing(self):
        """7c"""
        logging.info("Regulatory codes select")

        if config.only_category:
            reg_codes = None
        else:
            reg_codes = config.input_df["regulatory_code"]
            reg_codes = reg_codes.unique().tolist()
            reg_codes.sort()
            reg_codes = RegCodesGUI(reg_codes).get_response()

        logging.info("Initial processing")
        self.processed_df = InitialProcessing(
            config.input_df, self.epgs, reg_codes
        ).run()

        config.out.accdb.write(
            "01 - RTR Emiss Inventory With ICF Work", self.processed_df
        )
        config.out.accdb.write(
            "02 - Emiss Process Grp Abbr Xwalk", pd.DataFrame.from_dict(self.epg_pairs)
        )

    def source_ids_create(self):
        """7d"""
        logging.info("Creating source ids")
        self.processed_df = SourceIDs(self.processed_df).run()
        config.out.accdb.write(
            "04 - Final RTR-HEM Emiss Inventory Xwalk", self.processed_df
        )

    def multipathway_processing(self):
        """7e"""
        logging.info("Running multipathway processing queries")
        MultiPathwayProcessing(self.processed_df).run()

    def write_all_remaining_outputs(self):
        """7f"""
        logging.info("Writing outputs")
        config.out.run(self.processed_df)


if __name__ == "__main__":
    try:
        RTR2HEM()
        logging.info("Done!")
    except Exception as e:
        logging.exception(e)
        if config.out and os.path.exists(config.out.output_dir):
            shutil.rmtree(config.out.output_dir)
