import datetime
import configparser
import pandas as pd
import pypyodbc


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

static_xls = pd.ExcelFile(config["Static"]["static_files"])
