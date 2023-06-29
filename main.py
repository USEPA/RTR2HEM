import datetime, json
import configparser
import pandas as pd
import numpy as np
import pypyodbc
import sqlalchemy as sq
from GUI.epg_popup import EpgGUI
from GUI.regCodes_popup import RegCodesGUI

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

dont forget that the results get loaded into pre-existing templates!
"""


def to_bool(val):
    return str(val).lower() == "true"


config = configparser.RawConfigParser()
config.read("config.txt")
date = str(datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))

settings = config["Settings"]
src_cat_name = f"{settings['source_category_name']}{date}"
new_emission_abbr = to_bool(settings["create_new_emission_abbr"])
only_category_records = to_bool(settings["only_category_records"])
emission_type = settings["emission_type"]
create_src_ids = to_bool(settings["create_new_src_ids"])

# fetch input access table, TODO - is there a cleaner option?
input_fp = config["Inputs"]["file"]
input_table = config["Inputs"]["table"]
conn = pypyodbc.connect(
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + input_fp + ";"
)
input_df = pd.read_sql(f"SELECT * FROM [{input_table}]", conn)

static_df = pd.read_excel(config["Static"]["static_files"])


"""
7b
these names are taken from the "EMISSION_PROCESS_GROUP" column
eventually gets used for source IDs

uses: 
    module “02 Emiss Process Grps” 

TODO - add import option
"""
epgs = input_df["emission_process_group"]
epgs = epgs.replace("", np.nan).dropna().unique().tolist()
epgs.sort()
epgs = EpgGUI(epgs).get_response()

"""
7c
selecting a regulatory code, always include an empty option?
these names are taken from the "REGULATORY_CODE" column
this GUI does only shows up if "category and non-category records" is selected

uses:
    module “03 Initial Processing” 
    form "Form_frmRegSelections"
"""
reg_codes = input_df["regulatory_code"]
reg_codes = reg_codes.replace(np.nan, "").unique().tolist()
reg_codes.sort()
reg_codes = RegCodesGUI(reg_codes).get_response()

print("!")
