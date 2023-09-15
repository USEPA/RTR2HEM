import logging
from modules.utils import set_column


class HapEmissions:
    sort_by = ["ICFFacilityID", "ICFSourceID", "hem3_chemical_name"]

    columns = [
        "ICFFacilityID",
        "ICFSourceID",
        "hem3_chemical_name",
        "ICFModelEmissionTPY",
        "ICFCatLevelModeling",
    ]

    filename = "HAPEmis"
    template_name = "HEM4_HAP_Emiss_ICF"
    sheet_name = "Hap emissions"
    rowstart = 1

    def __init__(self, df):
        self.df = df

    def create(self):
        hap_emiss_df = self.df.copy()
        hap_emiss_df = hap_emiss_df.sort_values(self.sort_by)

        set_column(hap_emiss_df, "ICFModelEmissionTPY", self.set_SumEmissionTPY)

        # Category only
        cat_hap_emiss_df = hap_emiss_df.drop_duplicates(self.columns)
        cat_hap_emiss_df = hap_emiss_df.loc[
            hap_emiss_df["ICFCatLevelModeling"] == "Yes"
        ]

        self.columns.pop()  # remove ICFCatLevelModeling
        self.cat_df = cat_hap_emiss_df[self.columns]

        # Wholesale
        hap_emiss_df = hap_emiss_df.drop_duplicates(self.columns)
        self.whole_df = hap_emiss_df[self.columns]

        return self

    def set_SumEmissionTPY(self, row):
        val = float(row["ICFModelEmissionTPY"])
        if val < 9e-28 and val > 0:
            logging.warning(
                "Some emissions are too small for modeling (On the order of E-29 or smaller TPY).  Setting them to 0."
            )
            val = 0
        return val
