import os, shutil
import numpy as np
import pandas as pd
from modules.initial_processing import InitialProcessing
from modules.source_ids import SourceIDs
from modules.multipathway_processing import MultiPathwayProcessing
from modules.write_outputs import WriteOutputs
from modules.utils import get_static, config

from modules.GUI.settings import SettingsGUI
from modules.GUI.column_map import ColumnMapGUI
from modules.GUI.epg_popup import EpgGUI
from modules.GUI.regCodes_popup import RegCodesGUI


class RTR2HEM:
    def __init__(self):
        self.steps_to_7a()
        self.step_7b()
        self.step_7c()
        self.step_7d()
        self.step_7e()
        self.step_7f()

    def steps_to_7a(self):
        """1-7a"""
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

    def step_7b(self):
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

    def step_7c(self):
        if config.only_category:
            reg_codes = None
        else:
            reg_codes = config.input_df["regulatory_code"]
            reg_codes = reg_codes.unique().tolist()
            reg_codes.sort()
            reg_codes = RegCodesGUI(reg_codes).get_response()

        self.processed_df = InitialProcessing(
            config.input_df, self.epgs, reg_codes
        ).run()

        config.out.accdb.write(
            "01 - RTR Emiss Inventory With ICF Work", self.processed_df
        )
        config.out.accdb.write(
            "02 - Emiss Process Grp Abbr Xwalk", pd.DataFrame.from_dict(self.epg_pairs)
        )

    def step_7d(self):
        self.processed_df = SourceIDs(self.processed_df).run()
        config.out.accdb.write(
            "04 - Final RTR-HEM Emiss Inventory Xwalk", self.processed_df
        )

    def step_7e(self):
        MultiPathwayProcessing(self.processed_df).run()

    def step_7f(self):
        config.out.run(self.processed_df)


if __name__ == "__main__":
    try:
        RTR2HEM()
        print("Done!")
    except Exception as e:
        print(e)
        if config.out and os.path.exists(config.out.output_dir):
            shutil.rmtree(config.out.output_dir)
