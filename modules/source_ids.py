import pandas as pd
from modules.utils import Join, set_column, config


class SourceIDs:
    facility_counter = {}

    source_id_columns = [
        "ICFFacilityID",
        "emission_unit_id",
        "process_id",
        "emission_release_point_id",
    ]

    sort_by = ["ICFFacilityID", "ICFSourceID"]

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.src_list_df = self.df.copy()

    def str_counter(self, counter):
        zero_count = "0" * (4 - len(f"{counter}"))
        if len(f"{counter}") > 4:
            raise ValueError("Exceeded range of acceptible counter values")
        return f"{zero_count}{counter}"

    def reverse_str_counter(self, row):
        src_id = row["icfsourceid"]
        if not src_id:
            return 0
        counter_val = src_id[-4:]
        return int(counter_val)

    def run(self):
        self.src_list_df = self.src_list_df.drop_duplicates(self.source_id_columns)
        self.src_list_df = self.src_list_df.sort_values(self.source_id_columns)
        if config.srcid_import is not None:
            self.import_existing_src_ids()

        set_column(self.src_list_df, "ICFSourceID", self.create_source_id)
        self.remerge_src_ids()

        config.out.accdb.write(
            "03 - Source ID Xwalk", self.src_list_df[config.srcid_required]
        )
        return self.df

    def create_source_id(self, row):
        if row["ICFSourceID"]:
            return row["ICFSourceID"]

        f_id = row["ICFFacilityID"]
        self.facility_counter.setdefault(f_id, 0)
        self.facility_counter[f_id] += 1
        counter = self.facility_counter[f_id]

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

    def remerge_src_ids(self):
        # custom join can't preserve both suffixes
        self.df = pd.merge(
            left=self.df,
            right=self.src_list_df,
            on=[
                "ICFFacilityID",
                "emission_unit_id",
                "process_id",
                "emission_release_point_id",
            ],
            suffixes=("", "_tmp"),
        )
        self.df["ICFSourceID"] = self.df["ICFSourceID_tmp"]
        self.df = Join().drop_tmp(self.df)
        self.df = self.df.sort_values(self.sort_by).reset_index(drop=True)
        return self.df

    def import_existing_src_ids(self):
        # normalize column names
        cols = {}
        for c in self.src_list_df.columns:
            for c2 in config.srcid_import.columns:
                if c.lower() == c2.lower():
                    cols[c2] = c
        config.srcid_import = config.srcid_import.rename(columns=cols)

        # merge imported src ids
        self.src_list_df = pd.merge(
            left=self.src_list_df,
            right=config.srcid_import,
            on=[
                "ICFFacilityID",
                "emission_unit_id",
                "process_id",
                "emission_release_point_id",
            ],
            suffixes=("", "_tmp"),
        )
        self.src_list_df["ICFSourceID"] = self.src_list_df["ICFSourceID_tmp"]
        self.src_list_df = Join().drop_tmp(self.src_list_df)
        self.src_list_df = self.src_list_df.reset_index(drop=True)

        # initialize facility counter
        sort_by = ["icffacilityid", "srcid_tmp"]
        set_column(config.srcid_import, "srcid_tmp", self.reverse_str_counter)
        result = config.srcid_import[sort_by].sort_values(sort_by, ascending=False)
        result = result.drop_duplicates("icffacilityid")

        facility_ids = result["icffacilityid"].tolist()
        src_id_vals = result["srcid_tmp"].tolist()
        self.facility_counter = dict(zip(facility_ids, src_id_vals))
