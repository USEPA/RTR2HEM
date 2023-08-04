import os
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


def calc_agg(df, group_by, agg, on_column, rename_column=None):
    tmp = df.copy()
    if group_by:
        tmp = tmp.groupby(group_by, as_index=False)
    avg_result = tmp[on_column].agg(agg)
    if rename_column:
        avg_result = avg_result.rename(columns={on_column: rename_column})
    return avg_result


def cross_product(df1, df2):
    df1["_key"] = 0
    df2["_key"] = 0
    return pd.merge(df1, df2, on="_key").drop("_key", axis=1)


def join(dfs, common_columns):
    if len(dfs[0].index) != len(dfs[1].index):
        print("Joining on a different number of rows!")
    result = pd.merge(dfs[0], dfs[1], on=common_columns)
    num_rows = len(result.index)

    for i in range(2, len(dfs)):
        if len(dfs[1].index) != num_rows:
            print("Joining on a different number of rows!")
        result = pd.merge(result, dfs[i], on=common_columns)
    return result


def get_static(filename):
    static_fp = os.path.join(static_dir, f"{filename}.xlsx")
    df = pd.read_excel(static_fp, "static")
    df.columns = df.columns.str.lower()
    return df.fillna("")


################################

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

static_dir = config["inputs"]["static"]
