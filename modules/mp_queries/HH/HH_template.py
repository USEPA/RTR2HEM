import pandas as pd
from modules.utils import calc_agg, cross_product, get_static

"""
template of every facility + every chemical

sheets:
    working_MP04HH_T1ChemResults
    working_MPHH_ChemEmissSums
"""


class Template:
    working_MP04HH_T1ChemResults = None
    working_MPHH_ChemEmissSums = None

    def __init__(self, df, latlons):
        self.df = df
        self.latlons = latlons

        self.qryMP04aHH_CreateShellForChemSVs()
        self.qryMP04bHH_CalcChemSums()
        self.qryMP04cHH_PopulateChemSVs()

    # working_MP04HH_T1ChemResults
    def qryMP04aHH_CreateShellForChemSVs(self):
        HHEquivalencyFactors = get_static(
            "static_MP_PBHAPChems_withHHEquivalencyFactors"
        )
        HHScreeningThresholds = get_static("static_MP_HHScreeningThresholds")

        tmp = pd.merge(
            left=HHEquivalencyFactors,
            right=HHScreeningThresholds,
            how="inner",
            left_on="shortpb-hap/ecohapname",
            right_on="shortpb-hapname",
        )
        tmp = cross_product(self.latlons.avg_lat_longs, tmp)

        # column cleaning
        group_by = {
            "Facility ID": "Facility ID",
            "Avg Lat": "Lat",
            "Avg Long": "Long",  # END avg_lat_long_columns
            "shortpb-hap/ecohapname": "PB-HAP Grp",
            "chem name for tier 2 tool": "Chem",
            "tef": "TEF (chem)",
            "eef": "EEF (chem)",
            "ref": "REF (chem)",
            "date pb-hap ref created": "Date REF Created",  # END HHEquivalencyFactors_columns
            "tier 1 screening threshold (tpy)": "Scrn Thresh (TPY; grp)",
            "date threshold created": "Date Scrn Thresh Created",  # END HHScreeningThresholds_columns
        }
        order_by = [
            "Facility ID",
            "shortpb-hap/ecohapname",
            "chem name for tier 2 tool",
        ]

        tmp = tmp[list(group_by.keys())].drop_duplicates()
        tmp = tmp.sort_values(order_by)

        tmp.insert(0, "Src Cat", "")
        tmp.insert(6, "Emiss (TPY; chem)", 0)
        tmp.insert(11, "Emiss*REF (TPY; chem)", 0)
        tmp.insert(14, "SV (chem)", 0)

        tmp = tmp.rename(columns=group_by)
        self.working_MP04HH_T1ChemResults = tmp

    # working_MPHH_ChemEmissSums
    def qryMP04bHH_CalcChemSums(self):
        group_by = ["ICFFacilityID", "chem name for tier 2 tool", "ICFCatLevelModeling"]

        tmp = self.df.loc[
            (self.df["chem name for tier 2 tool"] != "")
            & (self.df["ICFCatLevelModeling"] == "Yes")
        ]

        tmp = calc_agg(
            tmp, group_by, "sum", "ICFModelEmissionTPY", "SumOfICFModelEmissionTPY"
        )

        tmp = tmp.drop("ICFCatLevelModeling", axis=1)
        self.working_MPHH_ChemEmissSums = tmp

    # working_MP04HH_T1ChemResults
    def qryMP04cHH_PopulateChemSVs(self):
        result = pd.merge(
            self.working_MP04HH_T1ChemResults,
            self.working_MPHH_ChemEmissSums,
            how="left",
            left_on=["Chem", "Facility ID"],
            right_on=["chem name for tier 2 tool", "ICFFacilityID"],
        )
        result = result.fillna(0)

        result["Emiss (TPY; chem)"] = result["SumOfICFModelEmissionTPY"]

        result["Emiss*REF (TPY; chem)"] = (
            result["SumOfICFModelEmissionTPY"] * result["REF (chem)"]
        )

        result["SV (chem)"] = (
            result["SumOfICFModelEmissionTPY"]
            * result["REF (chem)"]
            / result["Scrn Thresh (TPY; grp)"]
        )

        result = result.drop(self.working_MPHH_ChemEmissSums.columns, axis=1)
        self.working_MP04HH_T1ChemResults = result
