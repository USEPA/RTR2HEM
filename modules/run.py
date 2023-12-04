import os
import json
import logging
import numpy as np
import pandas as pd

from modules.queries.QA import run_qa
from modules import (
    InitialProcessing,
    SourceIDs,
    MultiPathwayProcessing,
    WriteOutputs,
)

from modules.GUI import statusGUI, ColumnMapGUI, EpgGUI, RegCodesGUI
from modules.utils import get_static, config


class RTR2HEM:
    def __init__(self, base, map_columns):
        self.base = base
        self.map_columns = map_columns

        self.columns_select()
        self.epgs_select()
        self.reg_codes_select()

        self.status = statusGUI(self.base)

        if config.run_qa:
            self.status.update("Running QA...")
            run_qa()
        self.initial_processing()
        self.source_ids_create()
        if config.emission_type != "Acute":
            self.multipathway_processing()
        self.write_all_remaining_outputs()

        config.out.accdb.close_accdb()
        self.status.update("")
        self.status.note("Status", "Run complete!")

    def columns_select(self):
        """1-7a"""
        logging.info("Columns select")

        # loaded from interface
        if self.map_columns:
            ColumnMapGUI(self.base)

        logging.debug(
            json.dumps({"settings": config.settings, "columns_map": config.columns_map})
        )

        config.out = WriteOutputs()
        config.rename_columns()
        config.set_input_df_column_types()

        config.out.accdb.write(
            "00 - RTR-HEM and PBHAP Poll Xwalk",
            get_static("static_PollutantCrosswalk_andMetalSpeciations"),
        )

        if config.emission_type != "Acute":
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
            epgs = EpgGUI(self.base, epgs).get_response()

        self.epgs = epgs
        self.epg_pairs = {
            config.epg_required[0]: list(epgs.keys()),
            config.epg_required[1]: list(epgs.values()),
        }

    def reg_codes_select(self):
        """7c"""
        logging.info("Regulatory codes select")

        reg_codes = config.input_df["regulatory_code"]
        reg_codes = reg_codes.unique().tolist()
        reg_codes.sort()
        if config.only_category:
            reg_codes = dict(zip(reg_codes, [1] * len(reg_codes)))
        else:
            reg_codes = RegCodesGUI(self.base, reg_codes).get_response()

        config.reg_codes = reg_codes

    def initial_processing(self):
        """7c"""
        logging.info("Initial processing")
        self.status.update("Initial processing...")

        self.processed_df = InitialProcessing(
            config.input_df, self.epgs, config.reg_codes
        ).run()

        # config.out.accdb.write(
        #    "01 - RTR Emiss Inventory With ICF Work", self.processed_df
        # )
        config.out.accdb.write(
            "02 - Emiss Process Grp Abbr Xwalk", pd.DataFrame.from_dict(self.epg_pairs)
        )

    def source_ids_create(self):
        """7d"""
        logging.info("Creating source ids")
        self.status.update("Creating source ids...")

        self.processed_df = SourceIDs(self.processed_df).run()
        config.out.accdb.write(
            "04 - Final RTR-HEM Emiss Inventory Xwalk", self.processed_df
        )

    def multipathway_processing(self):
        """7e"""
        logging.info("Running multipathway processing queries")
        mp_queries = MultiPathwayProcessing(self.processed_df)

        self.status.update("Running multipathway processing \nqueries (HumHealth)...")
        mp_queries.run_HH()

        self.status.update("Running multipathway processing \nqueries (Eco)...")
        mp_queries.run_Eco()

    def write_all_remaining_outputs(self):
        """7f"""
        logging.info("Writing outputs")
        self.status.update("Writing remaining outputs...")
        config.out.run(self.processed_df)

        user_settings = {"settings": config.settings, "columns_map": config.columns_map}
        fp = os.path.join(
            config.out.output_dir,
            f"{config.out.runname}_config_{config.timestamp}.json",
        )
        with open(fp, "w") as fh:
            json.dump(user_settings, fh)
