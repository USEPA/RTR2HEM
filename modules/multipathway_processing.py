from modules.utils import calc_agg, cross_product, get_static, set_column
import pandas as pd

"""
TODO
- move overrides out
- split into
    - latitudes/longitudes
    - HH
    - Eco

"createshell" creates that template of every facility + every chem. then downstream queries populate it with numbers, for the specific chems emitted by the specific facilities

ONLY run this on actual/allowable emissions, NOT acute

For each query: in the side menu right click > design view > right click the tab at the top select "sql view"
"data sheet" view will show you what the resulting df should look like
"""


class MultiPathwayProcessing:
    def __init__(self, df):
        self.df = df.copy()

    def run(self):
        self.qryMP00aEco_DuplicateCrosswalkInventory()
        self.qryMP00bEco_AddDivalentMercury()

        self.qryMP03a_SourceLatLons_CatLevel()
        self.qryMP03aa_LineLatLons01()
        self.qryMP03aa_LineLatLons02()
        self.qryMP03ab_AppendLineLatLongs()

        self.qryMP04aHH_CreateShellForChemSVs()
        self.qryMP04bHH_CalcChemSums()
        self.qryMP04cHH_PopulateChemSVs()

        self.qryMP04dEco_CreateShellForChemSVs()
        return self.df

    # working_CrosswalkEmissionInventory_Eco
    def qryMP00aEco_DuplicateCrosswalkInventory(self):
        self.working_CrosswalkEmissionInventory_Eco = self.df.copy()

    # working_CrosswalkEmissionInventory_Eco
    def qryMP00bEco_AddDivalentMercury(self):
        tmp = self.working_CrosswalkEmissionInventory_Eco
        tmp = tmp.loc[
            tmp["chem name for tier 2 tool"] == "Methyl Mercury (Emitted as Divalent)"
        ]
        self.working_CrosswalkEmissionInventory_Eco = tmp

    # working_MPLatLongs
    def qryMP03a_SourceLatLons_CatLevel(self):
        columns = {
            "ICFFacilityID": "Facility ID",
            "sppd_facility_identifier": "sppd_facility_identifier",
            "ICFSourceID": "Source ID",
            "y_coordinate": "Latitude",
            "x_coordinate": "Longitude",
            "ICFCatLevelModeling": "ICFCatLevelModeling",
        }
        key_cols = list(columns.keys())

        # keep an eye out on cells that could be classified as NaN instead of ""
        tmp = self.df[key_cols].drop_duplicates()
        tmp = tmp.sort_values(key_cols)
        tmp = tmp.loc[
            (tmp["y_coordinate"] != "")
            & (tmp["x_coordinate"] != "")
            & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        del columns["ICFCatLevelModeling"]
        self.working_MPLatLongs = tmp[list(columns.keys())].rename(columns=columns)

    # working_MPLatLongsLine
    # TODO -- get working data for this
    def qryMP03aa_LineLatLons01(self):
        columns = {
            "ICFFacilityID": "Facility ID",
            "sppd_facility_identifier": "sppd_facility_identifier",
            "fugitive_2d_midpoint1_y_coordinate": "LineLatitude",
            "fugitive_2d_midpoint1_x_coordinate": "LineLongitude",
            "ICFCatLevelModeling": "ICFCatLevelModeling",
            "ICFSourceType": "ICFSourceType",
        }
        key_cols = list(columns.keys())

        tmp = self.df[key_cols].drop_duplicates()
        tmp = tmp.sort_values(key_cols)
        tmp = tmp.loc[
            (tmp["ICFSourceType"] == "N") & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        del columns["ICFCatLevelModeling"]
        del columns["ICFSourceType"]
        tmp = tmp[list(columns.keys())]

        self.working_MPLatLongsLine = tmp.rename(columns=columns)

    # working_MPLatLongsLine
    # TODO -- get working data for this
    def qryMP03aa_LineLatLons02(self):
        columns = {
            "ICFFacilityID": "Facility ID",
            "sppd_facility_identifier": "sppd_facility_identifier",
            "fugitive_2d_midpoint2_y_coordinate": "LineLatitude",
            "fugitive_2d_midpoint2_x_coordinate": "LineLongitude",
            "ICFCatLevelModeling": "ICFCatLevelModeling",
            "ICFSourceType": "ICFSourceType",
        }
        key_cols = list(columns.keys())

        tmp = self.df[key_cols].drop_duplicates()
        tmp = tmp.sort_values(key_cols)
        tmp = tmp.loc[
            (tmp["ICFSourceType"] == "N") & (tmp["ICFCatLevelModeling"] == "Yes")
        ]

        del columns["ICFCatLevelModeling"]
        del columns["ICFSourceType"]
        tmp = tmp[list(columns.keys())]

        tmp = tmp.rename(columns=columns)
        self.working_MPLatLongsLine = pd.concat(
            [self.working_MPLatLongsLine, tmp], ignore_index=True
        )

    # working_MPLatLongs
    # TODO -- get working data for this
    def qryMP03ab_AppendLineLatLongs(self):
        group_by = ["Facility ID", "sppd_facility_identifier", "Source ID"]

        if not self.working_MPLatLongsLine.empty:
            avg_lat = calc_agg(
                self.working_MPLatLongsLine,
                group_by,
                "mean",
                "LineLatitude",
                "Latitude",
            )
            avg_long = calc_agg(
                self.working_MPLatLongsLine,
                group_by,
                "mean",
                "LineLongitude",
                "Longitude",
            )
            result = pd.merge(avg_lat, avg_long, on=group_by)

            self.working_MPLatLongs = pd.concat(
                [self.working_MPLatLongs, result], ignore_index=True
            )

    # working_MPLatLongs
    # helper method for qryMP04aHH
    def qryMP03b_Avg_SourceLatLons_CatLevel(self):
        group_by = ["Facility ID", "sppd_facility_identifier"]

        avg_lat = calc_agg(
            self.working_MPLatLongs, group_by, "mean", "Latitude", "Avg Lat"
        )
        avg_long = calc_agg(
            self.working_MPLatLongs, group_by, "mean", "Longitude", "Avg Long"
        )

        result = pd.merge(avg_lat, avg_long, on=group_by)
        return result

    # working_MP04HH_T1ChemResults
    def qryMP04aHH_CreateShellForChemSVs(self):
        HHEquivalencyFactors = get_static(
            "static_MP_PBHAPChems_withHHEquivalencyFactors"
        )
        HHScreeningThresholds = get_static("static_MP_HHScreeningThresholds")
        avg_lat_long = self.qryMP03b_Avg_SourceLatLons_CatLevel()

        tmp = pd.merge(
            left=HHEquivalencyFactors,
            right=HHScreeningThresholds,
            how="inner",
            left_on="shortpb-hap/ecohapname",
            right_on="shortpb-hapname",
        )
        tmp = cross_product(avg_lat_long, tmp)

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
    # TODO -- verify more closely that this is working as intended
    def qryMP04cHH_PopulateChemSVs(self):
        """
        UPDATE working_MP04HH_T1ChemResults

        INNER JOIN working_MPHH_ChemEmissSums ON
        (working_MP04HH_T1ChemResults.Chem = working_MPHH_ChemEmissSums.[Chem Name For Tier 2 Tool])
        AND (working_MP04HH_T1ChemResults.[Facility ID] = working_MPHH_ChemEmissSums.ICFFacilityID)

        SET working_MP04HH_T1ChemResults.[Emiss (TPY; chem)] = [SumOfICFModelEmissionTPY],
        working_MP04HH_T1ChemResults.[Emiss*REF (TPY; chem)] = [SumOfICFModelEmissionTPY]*[REF (chem)],
        working_MP04HH_T1ChemResults.[SV (chem)] = [SumOfICFModelEmissionTPY]*[REF (chem)]/[Scrn Thresh (TPY; grp)];
        """
        self.working_MP04HH_T1ChemResults = pd.merge(
            self.working_MP04HH_T1ChemResults,
            self.working_MPHH_ChemEmissSums,
            how="inner",
            left_on=["Chem", "Facility ID"],
            right_on=["chem name for tier 2 tool", "ICFFacilityID"],
        )

        def update_emiss(row):
            return row["SumOfICFModelEmissionTPY"]

        def update_emiss_ref(row):
            return row["SumOfICFModelEmissionTPY"] * row["REF (chem)"]

        def update_sv(row):
            return (
                row["SumOfICFModelEmissionTPY"]
                * row["REF (chem)"]
                / row["Scrn Thresh (TPY; grp)"]
            )

        set_column(self.working_MP04HH_T1ChemResults, "Emiss (TPY; chem)", update_emiss)
        set_column(
            self.working_MP04HH_T1ChemResults, "Emiss*REF (TPY; chem)", update_emiss_ref
        )
        set_column(self.working_MP04HH_T1ChemResults, "SV (chem)", update_sv)

        self.working_MP04HH_T1ChemResults = self.working_MP04HH_T1ChemResults.drop(
            self.working_MPHH_ChemEmissSums.columns, axis=1
        )

    def qryMP04dEco_CreateShellForChemSVs(self):
        pass
