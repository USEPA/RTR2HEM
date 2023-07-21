import datetime
import json
import pandas as pd
import pypyodbc


def to_bool(val):
    return str(val).lower() == "true"


def set_column(df, column_name, func):
    df[column_name] = df.apply(lambda row: func(row), axis=1)


def get_col(name, df=None):
    """Gets mapped column name and attempts case insensitive lookup"""
    response = columns_map.get(name.lower(), None)
    if response == None:
        raise KeyError(f"{name} could not be found in mapping")
    elif response == "":
        response = name.lower()
    response = response if response else name

    if df is None:
        return response
    else:
        try:
            if response in df:
                return df[response]
            return df[response.lower()]
        except:
            raise Exception(
                f'Column "{response}" could not be found in the provided dataframe'
            )


def get_xls_sheet(sheet_name):
    return pd.read_excel(static_xls, sheet_name)


with open(".\config.json") as fh:
    config = json.load(fh)

settings = config["settings"]
timestamp = str(datetime.datetime.now().strftime("%Y%m%d"))
src_cat_name = settings["source_category_name"]
emission_type = settings["emission_type"]
only_category = settings["only_category_records"]

columns_map = config["processing_columns"]["pre"]
columns_map = {k.lower(): v for k, v in columns_map.items()}
postprocessing_columns = config["processing_columns"]["post"]

# fetch input access table
input_fp = config["inputs"]["input_file"]
input_table = config["inputs"]["input_table"]

odbc_string = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + input_fp + ";"
conn = pypyodbc.connect(odbc_string)
input_df = pd.read_sql(f"SELECT * FROM [{input_table}]", conn)

static_xls = pd.ExcelFile(config["inputs"]["static"])
