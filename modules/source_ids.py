from .utils import set_column


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
        set_column(self.df, "ICFSourceID", self.create_source_id)
        return self.df

    def create_source_id(self, row):
        f_id = row["ICFFacilityID"]
        self.facilty_counter.setdefault(f_id, 0)
        self.facilty_counter[f_id] += 1
        counter = self.facilty_counter[f_id]

        erp_type = row["emission_release_point_type"]
        erp_type = f"0{erp_type}" if len(erp_type) == 1 else f"{erp_type}"

        if row["ICFCatLevelModeling"]:
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
