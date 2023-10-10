import pandas as pd
from modules.utils import Join, calc_agg, get_static

"""
template of every facility + every chemical

sheets:
    working_MP04Eco_T1ChemResults
    working_MPEco_ChemEmissSums
"""


class Template:
    working_MP04Eco_T1ChemResults = None
    working_MPEco_ChemEmissSums = None

    def __init__(self, working_crosswalk, eco_crosswalk, latlons):
        self.working_crosswalk = working_crosswalk
        self.eco_crosswalk = eco_crosswalk
        self.latlons = latlons

        self.qry_04dEco_CreateShellForChemSVs()
        self.qry_04eEco_CalcChemSums()
        self.qry_04fEco_PopulateChemSVs()

    # working_MP04Eco_T1ChemResults
    def qry_04dEco_CreateShellForChemSVs(self):
        EcoEquivalencyFactors = get_static("static_MP_EcoEquivalencyFactors")
        EcoScreeningThresholds = get_static("static_MP_EcoScreeningThresholds")

        tmp = Join().join(
            left=EcoEquivalencyFactors,
            right=EcoScreeningThresholds,
            how="inner",
            on=["assessment endpoint", "shortpb-hap/ecohapname"],
        )
        tmp = Join().cross_product(self.latlons.avg_lat_longs, tmp)

        # column cleaning
        group_by = {
            "Facility ID": "Facility ID",
            "Avg Lat": "Lat",
            "Avg Long": "Long",  # END avg_lat_long_columns
            "shortpb-hap/ecohapname": "EcoHAP Grp",
            "chem name for tier 2 tool": "Chem",
            "assessment endpoint": "assessment endpoint",
            "ecoeef": "EcoEEF (chem)",
            "date of ecoeef creation": "Date EcoEEF Created",
            "benchmark effects level": "benchmark effects level",
            "benchmark value": "benchmark value",
            "tier 1 eco screening threshold (tpy)": "Scrn Thresh (TPY; grp)",
            "date threshold created": "Date Scrn Thresh Created",
        }
        order_by = [
            "Facility ID",
            "shortpb-hap/ecohapname",
            "chem name for tier 2 tool",
            "assessment endpoint",
            "benchmark effects level",
            "benchmark value",
        ]

        tmp = tmp[list(group_by.keys())].drop_duplicates()
        tmp = tmp.sort_values(order_by)

        tmp.insert(0, "Src Cat", "")
        tmp.insert(6, "Emiss (TPY; chem)", 0)
        tmp.insert(10, "Emiss*EcoEEF (TPY; chem)", 0)
        tmp.insert(15, "SV (chem)", 0)

        tmp = tmp.rename(columns=group_by)
        self.working_MP04Eco_T1ChemResults = tmp

    # working_MPEco_ChemEmissSums
    def qry_04eEco_CalcChemSums(self):
        group_by = ["ICFFacilityID", "chem name for tier 2 tool", "ICFCatLevelModeling"]

        tmp = self.eco_crosswalk.loc[
            (self.eco_crosswalk["chem name for tier 2 tool"] != "")
            & (self.eco_crosswalk["ICFCatLevelModeling"] == "Yes")
        ]

        tmp = calc_agg(
            tmp, group_by, "sum", "ICFModelEmissionTPY", "SumOfICFModelEmissionTPY"
        )

        tmp = tmp.drop("ICFCatLevelModeling", axis=1)
        self.working_MPEco_ChemEmissSums = tmp

    # working_MP04Eco_T1ChemResults
    def qry_04fEco_PopulateChemSVs(self):
        result = Join().join(
            left=self.working_MP04Eco_T1ChemResults,
            right=self.working_MPEco_ChemEmissSums,
            how="left",
            left_on=["Facility ID", "Chem"],
            right_on=["ICFFacilityID", "chem name for tier 2 tool"],
        )
        result = result.fillna(0)

        result["Emiss (TPY; chem)"] = result["SumOfICFModelEmissionTPY"]

        result["Emiss*EcoEEF (TPY; chem)"] = (
            result["SumOfICFModelEmissionTPY"] * result["EcoEEF (chem)"]
        )

        result["SV (chem)"] = (
            result["SumOfICFModelEmissionTPY"]
            * result["EcoEEF (chem)"]
            / result["Scrn Thresh (TPY; grp)"]
        )

        result = result.drop(self.working_MPEco_ChemEmissSums.columns, axis=1)

        sort_by = [
            "Facility ID",
            "Chem",
            "assessment endpoint",
            "benchmark effects level",
        ]
        result = result.sort_values(sort_by)
        self.working_MP04Eco_T1ChemResults = result
