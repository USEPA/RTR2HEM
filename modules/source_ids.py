import pandas as pd
from .utils import set_column, source_id_columns


class SourceIDs:
    facilty_counter = {}

    def __init__(self, df):
        self.df = df
        self.df["ICFSourceID"] = ""

    def str_counter(self, counter):
        zero_count = "0" * (4 - len(f"{counter}"))
        if len(f"{counter}") > 4:
            raise ValueError("Exceeded range of acceptible counter values")
        return f"{zero_count}{counter}"

    def run(self):
        source_list_df = self.df.drop_duplicates(source_id_columns)
        source_list_df = source_list_df.sort_values(source_id_columns)
        set_column(source_list_df, "ICFSourceID", self.create_source_id)

        self.remerge_src_ids(self.df, source_list_df)
        return self.df

    def create_source_id(self, row):
        f_id = row["ICFFacilityID"]
        self.facilty_counter.setdefault(f_id, 0)
        self.facilty_counter[f_id] += 1
        counter = self.facilty_counter[f_id]

        erp_type = row["emission_release_point_type"]
        erp_type = f"0{erp_type}" if len(erp_type) == 1 else f"{erp_type}"

        if row["ICFCatLevelModeling"] == "Yes":
            if not row["emission_process_group"]:
                source_id = "C_" + erp_type + self.str_counter(counter)
            else:
                source_id = (
                    "CE"
                    + row["ICFEmissionProcessGroupAbbr"]
                    + self.str_counter(counter)
                )
        else:
            if row["ICFEmissionProcessGroupAbbr"]:
                source_id = (
                    "NE"
                    + row["ICFEmissionProcessGroupAbbr"]
                    + self.str_counter(counter)
                )
            else:
                source_id = "N_" + erp_type + self.str_counter(counter)

        assert len(source_id) == 8
        return source_id

    def remerge_src_ids(self, df, source_list):
        df = pd.merge(
            self.df,
            source_list,
            on=source_id_columns,
            suffixes=("tmp", ""),
        )
        for c in df.columns:
            if "tmp" in c:
                self.df = df.drop(c, axis=1)
