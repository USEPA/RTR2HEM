from src.utils import calc_agg
import pandas as pd

"""
sheets:
    working_MPLatLongs
    working_MPLatLongsLine
"""


class LatLons:
    working_MPLatLongs = None
    working_MPLatLongsLine = None
    avg_lat_longs = None

    def __init__(self, df):
        self.df = df

        self.qry_03a_SourceLatLons_CatLevel()
        self.qry_03aa_LineLatLons01()
        self.qry_03aa_LineLatLons02()

        self.qry_03b_Avg_SourceLatLons_CatLevel()

    # working_MPLatLongs
    def qry_03a_SourceLatLons_CatLevel(self):
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
    def qry_03aa_LineLatLons01(self):
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
    def qry_03aa_LineLatLons02(self):
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
    def qry_03ab_AppendLineLatLongs(self):
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
    # helper method for qry_04aHH
    def qry_03b_Avg_SourceLatLons_CatLevel(self):
        group_by = ["Facility ID", "sppd_facility_identifier"]

        avg_lat = calc_agg(
            self.working_MPLatLongs, group_by, "mean", "Latitude", "Avg Lat"
        )
        avg_long = calc_agg(
            self.working_MPLatLongs, group_by, "mean", "Longitude", "Avg Long"
        )

        self.avg_lat_longs = pd.merge(avg_lat, avg_long, on=group_by)
