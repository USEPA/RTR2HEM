import numpy as np
from GUI.epg_popup import EpgGUI
from GUI.regCodes_popup import RegCodesGUI
from modules.initial_processing import InitialProcessing
from modules.source_ids import SourceIDs
from modules.utils import get_col, input_df, columns_map

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

for name in columns_map:
    if columns_map[name]:
        print(f"Column {name} is set with override {columns_map[name]}")

# preprocessing
for column in input_df.columns:
    if column != get_col("regulatory_code") and column != get_col(
        "emission_process_group"
    ):
        input_df[column].fillna(0, inplace=True)


"""
7b
these names are taken from the "EMISSION_PROCESS_GROUP" column
eventually gets used for source IDs

uses: 
    module “02 Emiss Process Grps” 

TODO - add import option
"""
epgs = get_col("emission_process_group", input_df)
epgs = epgs.replace("", np.nan).dropna().unique().tolist()
epgs.sort()
epgs = EpgGUI(epgs).get_response()

"""
7c
these names are taken from the "REGULATORY_CODE" column
this GUI does only shows up if "category and non-category records" is selected

uses:
    module “03 Initial Processing” 
    form "Form_frmRegSelections"
"""
reg_codes = get_col("regulatory_code", input_df)
reg_codes = reg_codes.replace(np.nan, "").unique().tolist()
reg_codes.sort()
reg_codes = RegCodesGUI(reg_codes).get_response()

processed_df = InitialProcessing(input_df, epgs, reg_codes).run()
processed_df = SourceIDs(processed_df).run()

print("!")
