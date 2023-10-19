import os, sys, pathlib
import logging
import datetime
import json
import warnings

import pandas as pd
import numpy as np

from modules.handle_accdb import AccdbHandle


# write to file if running in an executable
if getattr(sys, "frozen", False):
    logging.basicConfig(
        filename="log.txt",
        filemode="w",
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
        format="[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s: %(message)s",
    )
else:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
        format="[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s: %(message)s",
    )
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def get_static(filename):
    static_fp = os.path.join(config.static_dir, f"{filename}.xlsx")
    df = pd.read_excel(static_fp, "static")
    df.columns = df.columns.str.lower()
    return df.fillna("")


def set_column(df, column_name, func):
    df[column_name] = df.apply(lambda row: func(row), axis=1)


def group(df, group_by, only_group=False):
    # NOTE: not to be confused with pandas 'group_by'
    if not isinstance(group_by, list):
        group_by = [group_by]
    grp = df.drop_duplicates(group_by)
    if only_group:
        return grp[group_by]
    return grp


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

    NOTE
    empty + non-empty will always try to favor/produce a non-empty dataframe
    however sometimes an empty result dataframe may be desired

    join
        accepts a list of dataframes, all pd.merge arguments,
        optional:
            drop_dupe = 'left'|'right'

        this custom join is case insensitive for both column names
        and cell values

        empty dataframes will have unique columns moved to the first
        non-empty dataframe with cells initialized to 0
    """

    def cross_product(self, df1, df2):
        df1["_key"] = 0
        df2["_key"] = 0
        return pd.merge(df1, df2, on="_key").drop("_key", axis=1)

    def join(self, dfs=None, **kwargs):
        if dfs is None:
            dfs = []
        if "left" in kwargs:
            dfs = [kwargs.pop("left")] + dfs
        if "right" in kwargs:
            dfs += [kwargs.pop("right")]

        dfs = self._preserve_empty_df_columns(dfs)
        if len(dfs) == 1:
            return dfs[0]

        dfs, kwargs = self._setup_tmp(dfs, **kwargs)
        drop_dupe = kwargs.pop("drop_dupe", "right")
        if drop_dupe == "right":
            kwargs["suffixes"] = ("", "_tmp")
        else:
            kwargs["suffixes"] = ("_tmp", "")

        result = pd.merge(left=dfs[0], right=dfs[1], **kwargs)
        result = self._drop_tmp(result)
        for i in range(2, len(dfs)):
            result = pd.merge(left=result, right=dfs[i], **kwargs)
            result = self._drop_tmp(result)
        result = self._drop_tmp(result, True)
        return result

    def _drop_tmp(self, df, also_drop_cpy=False):
        for column in df.columns:
            try:
                if "_tmp" in column:
                    df = df.drop(column, axis=1)
                if also_drop_cpy and "_cpy" in column:
                    df = df.drop(column, axis=1)
            except:
                pass
        return df

    def _setup_tmp(self, dfs, **kwargs):
        """creates '_cpy' lowercase columns to be used for joining
        so that the original columns are not modified"""
        tmp_dfs = [df.copy() for df in dfs]
        dfs = tmp_dfs
        to_list = lambda val: val if isinstance(val, list) else [val]

        # columns to merge on
        on_col = to_list(kwargs.pop("on", []))
        left_on = to_list(kwargs.get("left_on", on_col))
        right_on = to_list(kwargs.get("right_on", on_col))
        if not left_on or not right_on:
            raise Exception("Missing columns to join on")

        # convert column names to lowercase
        left_cpy = [f"{item}_cpy".lower() for item in left_on]
        right_cpy = [f"{item}_cpy".lower() for item in right_on]

        # convert all rows in column_cpy to lowercase
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

    def _preserve_empty_df_columns(self, dfs):
        """copy unique columns from empty df before removing from the merge"""
        existing_columns = []
        empty_dfs = list(filter(lambda df: df.empty, dfs))
        dfs = list(filter(lambda df: not df.empty, dfs))
        for df in dfs:
            existing_columns += [f"{item}".lower() for item in df.columns]

        if not dfs:
            dfs = [pd.DataFrame()]

        for empty in empty_dfs:
            for col in empty.columns:
                if col.lower() not in existing_columns:
                    dfs[0][col] = 0
        return dfs


class Config:
    """
    Read in config settings, either by a .json input file or settings GUI
    """

    not_required = ["emission_process_group"]
    epg_required = ["emission_process_group", "ICFEmissionProcessGroupAbbr"]
    srcid_required = [
        "ICFFacilityID",
        "ICFSourceID",
        "emission_unit_id",
        "process_id",
        "emission_release_point_id",
        "emission_release_point_type",
        "regulatory_code",
        "ICFCatLevelModeling",
        "emission_process_group",
        "ICFEmissionProcessGroupAbbr",
    ]

    reg_codes = None

    # output writer
    out = None

    def __init__(self):
        pass

    def load_config(self, fp=".\config.json", obj=None):
        if not obj:
            with open(fp) as fh:
                self.config = json.load(fh)
            self.settings = self.config["settings"]
            self.columns_map = self.config["columns_map"]
        else:
            self.config = obj
            with open(fp) as fh:
                self.settings = self.config["settings"]
                self.columns_map = json.load(fh)["columns_map"]

        self.get_settings()
        self.get_imports()

    def get_settings(self):
        self.timestamp = str(datetime.datetime.now().strftime("%Y%m%d"))
        self.src_cat_name = self.settings["source_category_name"]
        self.output_dir = self.settings["output_dir"]
        if not self.output_dir:
            self.output_dir = os.getcwd()
        self.emission_type = self.settings["emission_type"]
        self.only_category = self.settings["only_category_records"]
        return self

    def get_imports(self):
        lower = lambda lst: [e.lower() for e in lst]

        self.input_fp = self.settings["input_file"]
        self.input_table = self.settings["input_table"]
        self.input_df = self.get_tables(self.input_fp, self.input_table)

        # EPGs -- optional
        self.epg_import = None
        epg = self.settings["emission_abbr"]
        if epg["import"]:
            self.epg_import = self.get_tables(epg["file"], epg["table"])
            self.epg_import = self.epg_import[lower(self.epg_required)]
            self.epg_import = self.epg_import.drop_duplicates()

        # Source IDs -- optional
        self.srcid_import = None
        srcid = self.settings["src_ids"]
        if srcid["import"]:
            self.srcid_import = self.get_tables(srcid["file"], srcid["table"])
            self.srcid_import = self.srcid_import[lower(self.srcid_required)]
            self.srcid_import = self.srcid_import.drop_duplicates()

        self.static_dir = self.settings["static"]
        return self

    def get_tables(self, filepath, tablename):
        """fetch input table"""
        ftype = pathlib.Path(filepath).suffix
        if ftype == ".xlsx":
            input_df = pd.read_excel(filepath, sheet_name=tablename)
        elif ftype == ".csv":
            input_df = pd.read_csv(filepath)
        else:
            accdb_reader = AccdbHandle(filepath, how="open")
            input_df = accdb_reader.accdb_to_df(tablename)
        return input_df

    def rename_columns(self):
        # NOTE -- may get weird if a column were to be renamed as an already existing column
        columns_map = {v.lower(): k for k, v in self.columns_map.items() if v}
        self.input_df = self.input_df.rename(columns=columns_map)

    def set_input_df_column_types(self):
        columns_int64 = []
        columns_float64 = [
            "stack_height (ft)",
            "exit_gas_temperature (f)",
            "stack_diameter (ft)",
            "exit_gas_velocity (ft/sec)",
            "fugitive_length_sigmax_ft",
            "fugitive_width_sigmay_ft",
            "x_coordinate",
            "y_coordinate",
            "fugitive_2d_midpoint1_y_coordinate",
            "fugitive_2d_midpoint2_y_coordinate",
            "fugitive_2d_midpoint1_x_coordinate",
            "fugitive_2d_midpoint2_x_coordinate",
        ]

        for c in self.input_df.columns:
            if c == "regulatory_code" or c == "emission_process_group":
                self.input_df[c].fillna("", inplace=True)
            else:
                self.input_df[c].fillna(0, inplace=True)

            if c in columns_int64:
                self.input_df[c] = self.input_df[c].astype(np.int64)
            elif c in columns_float64:
                self.input_df[c] = self.input_df[c].astype(np.float64)
            else:
                self.input_df[c] = self.input_df[c].astype(str)

        # exception for EIS input file
        if "emission_process_group" not in self.input_df.columns:
            self.input_df["emission_process_group"] = ""


config = Config()
