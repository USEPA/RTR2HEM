from modules.utils import set_column, config


class SourceIDs:
    facility_counter = {}

    source_id_columns = [
        "ICFFacilityID",
        "emission_unit_id",
        "process_id",
        "emission_release_point_id",
    ]

    def __init__(self, df):
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
        set_column(self.df, "ICFSourceID", self.merge_src_ids)

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

    def merge_src_ids(self, row):
        src = self.src_list_df
        result = self.src_list_df.loc[
            (src["ICFFacilityID"] == row["ICFFacilityID"])
            & (src["emission_unit_id"] == row["emission_unit_id"])
            & (src["process_id"] == row["process_id"])
            & (src["emission_release_point_id"] == row["emission_release_point_id"])
        ]
        assert len(result) == 1
        return result.iloc[0]["ICFSourceID"]

    def import_existing_src_ids(self):
        def merge_import_src_ids(row):
            src = config.srcid_import
            result = src.loc[
                (src["icffacilityid"] == row["ICFFacilityID"])
                & (src["emission_unit_id"] == row["emission_unit_id"])
                & (src["process_id"] == row["process_id"])
                & (src["emission_release_point_id"] == row["emission_release_point_id"])
            ]
            if len(result) == 1:
                return result.iloc[0]["icfsourceid"]
            return ""

        set_column(self.src_list_df, "ICFSourceID", merge_import_src_ids)

        # init facility counter
        sort_by = ["icffacilityid", "srcid_tmp"]
        set_column(config.srcid_import, "srcid_tmp", self.reverse_str_counter)
        result = config.srcid_import[sort_by].sort_values(sort_by, ascending=False)
        result = result.drop_duplicates("icffacilityid")

        facility_ids = result["icffacilityid"].tolist()
        src_id_vals = result["srcid_tmp"].tolist()
        self.facility_counter = dict(zip(facility_ids, src_id_vals))
