from modules.queries.QA.qa_base import QABase
from modules.utils import group

"""
QA 04 - Latitude and Longitude Hemispheres: this QA checks that all latitures are positive and all longitudes are negative

qry_QA_04_Hemispheres - this query returns facilities with unexpected lat/long
"""


class Hemispheres(QABase):
    qa_num = "04"
    qa_title = "Latitude and Longitude Hemispheres"

    def run(self):
        num_invalid_lat_longs = self.qry_QA_04_Hemispheres()
        if num_invalid_lat_longs == 0:
            self.update(
                "Passed QA",
                "As expected, all records have positive latitude values (Y coordinates) and negative longitude values (X coordinates).",
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                Number of facilities with unexpected coordinate values: {num_invalid_lat_longs} 
                (unexpected latitudes are negative Y coordinates; unexpected longitudes are positive X coordinates). 
                If these coordinates are incorrect, then the risk modeling will be inaccurate or may fail. 
                See information in the "04" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program. 
                """,
                "qry_QA_04_Hemispheres",
            )
        return self

    def qry_QA_04_Hemispheres(self):
        group_by = [
            "sppd_facility_identifier",
            "city",
            "state_abbr",
            "y_coordinate",
            "x_coordinate",
            "fugitive_2d_midpoint1_y_coordinate",
            "fugitive_2d_midpoint2_y_coordinate",
            "fugitive_2d_midpoint1_x_coordinate",
            "fugitive_2d_midpoint2_x_coordinate",
        ]

        res = group(self.df, group_by, True)
        res = res.loc[
            (res["y_coordinate"] < 0)
            | (res["fugitive_2d_midpoint1_y_coordinate"] < 0)
            | (res["fugitive_2d_midpoint2_y_coordinate"] < 0)
            | (res["x_coordinate"] > 0)
            | (res["fugitive_2d_midpoint1_x_coordinate"] > 0)
            | (res["fugitive_2d_midpoint2_x_coordinate"] > 0)
        ]
        self.qa_df = res
        return len(res.index)
