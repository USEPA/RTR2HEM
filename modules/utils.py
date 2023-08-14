import os
import datetime
import json
import pandas as pd
import pypyodbc


def to_bool(val):
    return str(val).lower() == "true"


def get_static(filename):
    static_fp = os.path.join(static_dir, f"{filename}.xlsx")
    df = pd.read_excel(static_fp, "static")
    df.columns = df.columns.str.lower()
    return df.fillna("")


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
    """
    returns a dataframe with group_by and resulting on_column columns
    """
    result = df.copy()
    if group_by:
        result = result.groupby(group_by, as_index=False)
    result = result[on_column].agg(agg)
    if rename_column:
        result = result.rename(columns={on_column: rename_column})
    return result


class Join:
    """
    Custom dataframe joins

    join
        accepts a list of dataframes, normal pd.merge arguments,
        and drop_dupe='left'|'right'

        this custom join is case insensitive for both column names
        and cell values
    """

    def cross_product(self, df1, df2):
        df1["_key"] = 0
        df2["_key"] = 0
        return pd.merge(df1, df2, on="_key").drop("_key", axis=1)

    def join(self, dfs=None, **kwargs):
        def drop_tmp(df, also_drop_cpy=False):
            for column in df.columns:
                try:
                    if "_tmp" in column:
                        df = df.drop(column, axis=1)
                    if also_drop_cpy and "_cpy" in column:
                        df = df.drop(column, axis=1)
                except:
                    pass
            return df

        if "left" in kwargs:
            dfs = [kwargs.pop("left")]
        if "right" in kwargs:
            dfs += [kwargs.pop("right")]

        dfs, kwargs = self.setup_tmp_columns(dfs, **kwargs)
        drop_dupe = kwargs.pop("drop_dupe", "right")
        if drop_dupe == "right":
            kwargs["suffixes"] = ("", "_tmp")
        else:
            kwargs["suffixes"] = ("_tmp", "")

        result = pd.merge(left=dfs[0], right=dfs[1], **kwargs)
        result = drop_tmp(result)
        for i in range(2, len(dfs)):
            result = pd.merge(left=result, right=dfs[i], **kwargs)
            result = drop_tmp(result)
        result = drop_tmp(result, True)
        return result

    def setup_tmp_columns(self, dfs, **kwargs):
        """creates '_cpy' lowercase columns to be used for joining
        so that the original columns are not modified"""
        tmp_dfs = [df.copy() for df in dfs]
        dfs = tmp_dfs
        to_list = lambda val: val if isinstance(val, list) else [val]

        on_col = to_list(kwargs.pop("on", []))
        left_on = to_list(kwargs.get("left_on", on_col))
        right_on = to_list(kwargs.get("right_on", on_col))
        if not left_on or not right_on:
            raise Exception("Missing columns to join on")

        left_cpy = [f"{item}_cpy".lower() for item in left_on]
        right_cpy = [f"{item}_cpy".lower() for item in right_on]

        kwargs["left_on"] = left_cpy
        dfs[0][left_cpy] = dfs[0][left_on]
        for cpy_col in left_cpy:
            dfs[0][cpy_col] = dfs[0][cpy_col].astype(str).str.lower()

        kwargs["right_on"] = right_cpy
        for df in dfs[1:]:
            df[right_cpy] = df[right_on]
            for cpy_col in right_cpy:
                df[cpy_col] = df[cpy_col].astype(str).str.lower()
        return dfs, kwargs


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
