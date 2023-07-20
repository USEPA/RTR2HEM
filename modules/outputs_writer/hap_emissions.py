from modules.utils import set_column


class HapEmissions:
    sort_by = ["ICFFacilityID", "ICFSourceID", "hem3_chemical_name"]

    columns = [
        "ICFFacilityID",
        "ICFSourceID",
        "hem3_chemical_name",
        "ICFModelEmissionTPY",
    ]

    def __init__(self, df):
        self.df = df

    def create(self):
        hap_emiss_df = self.df.copy()
        hap_emiss_df = hap_emiss_df.sort_values(self.sort_by)
        hap_emiss_df = hap_emiss_df.drop_duplicates(self.columns)

        set_column(hap_emiss_df, "ICFModelEmissionTPY", self.set_SumEmissionTPY)

        cat_hap_emiss_df = hap_emiss_df.loc[
            hap_emiss_df["ICFCatLevelModeling"] == "Yes"
        ]

        hap_emiss_df = hap_emiss_df[self.columns]
        cat_hap_emiss_df = cat_hap_emiss_df[self.columns]

        return cat_hap_emiss_df, hap_emiss_df

    def set_SumEmissionTPY(self, row):
        val = float(row["ICFModelEmissionTPY"])
        if val < 9e-28 and val > 0:
            print(
                "Some emissions are too small for modeling (On the order of E-29 or smaller TPY).  Setting them to 0."
            )
            val = 0
        return val
        # return f'{val:.15f}'
