import numpy as np
import pandas as pd
from modules.initial_processing import InitialProcessing
from modules.source_ids import SourceIDs
from modules.multipathway_processing import MultiPathwayProcessing
from modules.write_outputs import WriteOutputs
from modules.utils import get_col, config

from modules.GUI.settings import SettingsGUI
from modules.GUI.column_map import ColumnMapGUI
from modules.GUI.epg_popup import EpgGUI
from modules.GUI.regCodes_popup import RegCodesGUI

"""
Demo refactories data settings

src_cat_name = "Refractories" + date
new_emission_abbr = True
only_category_records = False -- has "WholeFacility" in the filename
emission_type = 'Actual Emissions' -- this changes depending on what you want to process, this file has all 3
create_src_ids = True

input_table = "Refractories_WholeFacil_ATAGFormat_20200904(edited)"

both source category records and whole-facility records
has source category emissions of 4 of the 5 PB-HAPs (missing: dioxins) 
    but, only 2 ERPTs and the both map to modeling as point sources
reg code 63SSSSS
6 unique EPGs

dont forget that the results get loaded into pre-existing templates
"""
SettingsGUI()
ColumnMapGUI()  # TODO -- do we want to skip this if config selected ...?
config.out = WriteOutputs()


# preprocessing
for column in config.input_df.columns:
    if column != get_col("regulatory_code") and column != get_col(
        "emission_process_group"
    ):
        config.input_df[column].fillna(0, inplace=True)


"""
7b
"""
epgs = get_col("emission_process_group", config.input_df)
epgs = epgs.replace("", np.nan).dropna().unique().tolist()
epgs.sort()
epgs = dict(zip(epgs, [""] * len(epgs)))

# populate with import
if config.epg_import is not None:
    epg_import = config.epg_import.to_dict("records")
    for i, item in enumerate(epg_import):
        key = item["emission_process_group"]
        val = item["emissionprocessgroup_abbr"]
        epgs[key] = val

# epgs = EpgGUI(epgs).get_response()
# epg_pairs = {
#    config.epg_required[0]: list(epgs.keys()),
#    config.epg_required[1]: list(epgs.values()),
# }


"""
7c
these names are taken from the "REGULATORY_CODE" column

TODO
this GUI does only shows up if "category and non-category records" is selected

uses:
    module “03 Initial Processing” 
    form "Form_frmRegSelections"
"""
reg_codes = get_col("regulatory_code", config.input_df)
reg_codes = reg_codes.replace(np.nan, "").unique().tolist()
reg_codes.sort()
# reg_codes = RegCodesGUI(reg_codes).get_response()


######## DEBUG ##########
epgs = {
    "Conveying system transfer point": "AA",
    "Curing oven": "AB",
    "Induction furnace": "AC",
    "Lime Kiln and Cooler with common exhaust": "AD",
    "Periodic kiln": "AE",
    "Tunnel kiln": "AF",
}

reg_codes = {"": 0, "63AAAAA": 0, "63SSSSS": 1, "SLT-0001": 0}

epg_pairs = {
    config.epg_required[0]: list(epgs.keys()),
    config.epg_required[1]: list(epgs.values()),
}
#########################

processed_df = InitialProcessing(config.input_df, epgs, reg_codes).run()
config.out.accdb.write("01 - RTR Emiss Inventory With ICF Work", processed_df)
config.out.accdb.write(
    "02 - Emiss Process Grp Abbr Xwalk", pd.DataFrame.from_dict(epg_pairs)
)

# 7d
processed_df = SourceIDs(processed_df).run()
config.out.accdb.write("04 - Final RTR-HEM Emiss Inventory Xwalk", processed_df)

# 7e
MultiPathwayProcessing(processed_df).run()

# 7f
config.out.run(processed_df)

print("Done!")
