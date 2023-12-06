from modules.queries.QA.qa_base import QABase
from modules.utils import group

"""
'QA 11 - Parameters for Line Sources: this QA will check for appropriate parameters values for line sources, if present.

'qry_QA_11_LineParams - this query returns unique sources that have unexpected values for line source parameters
"""


class LineParams(QABase):
    qa_num = "11"
    qa_title = "Parameters for Line Sources"

    def run(self):
        num_sources_unexpected_vals = self.qry_QA_11b_LineParams()
        if num_sources_unexpected_vals == 0:
            self.update(
                "Passed QA",
                """
                All line sources (if present) have valid parameter values. 
                Evaluated fields include: STACK_HEIGHT (ft), which must have positive values (at least 2 meters [6.56168 feet] for buoyant line sources, 
                which are not designated separately from line sources in the modeling file), FUGITIVE_WIDTH_SIGMAY_FT, which must have positive values, 
                and FUGITIVE_2D_MIDPOINT1_X_COORDINATE, FUGITIVE_2D_MIDPOINT1_Y_COORDINATE, FUGITIVE_2D_MIDPOINT2_X_COORDINATE, 
                and FUGITIVE_2D_MIDPOINT2_Y_COORDINATE, which must have non-zero values.
                """,
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                Number of line sources with unexpected parameter values: {num_sources_unexpected_vals}. 
                These sources cannot be modeled with these unexpected parameter values. 
                Evaluated fields include: STACK_HEIGHT (ft), which must have positive values (at least 2 meters [6.56168 feet] for buoyant line sources, 
                which are not designated separately from line sources in the modeling file), FUGITIVE_WIDTH_SIGMAY_FT, which must have positive values, 
                and FUGITIVE_2D_MIDPOINT1_X_COORDINATE, FUGITIVE_2D_MIDPOINT1_Y_COORDINATE, FUGITIVE_2D_MIDPOINT2_X_COORDINATE, 
                and FUGITIVE_2D_MIDPOINT2_Y_COORDINATE, which must have non-zero values. 
                See information in the "11" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_11b_LineParams",
            )
        return self

    def qry_QA_11b_LineParams(self):
        group_by = [
            "sppd_facility_identifier",
            "emission_unit_id",
            "process_id",
            "emission_release_point_id",
            "emission_release_point_type",
            "regulatory_code",
            "stack_height (ft)",
            "fugitive_length_sigmax_ft",
            "fugitive_width_sigmay_ft",
            "y_coordinate",
            "x_coordinate",
            "fugitive_2d_midpoint1_y_coordinate",
            "fugitive_2d_midpoint2_y_coordinate",
            "fugitive_2d_midpoint1_x_coordinate",
            "fugitive_2d_midpoint2_x_coordinate",
            "emission_process_group",
        ]
        erp_types = ["9"]
        res = group(self.df, group_by, True)
        res = res.loc[
            (
                (res["stack_height (ft)"] < 6.56168)
                | (res["fugitive_width_sigmay_ft"] < 3.28084)
                | (res["fugitive_2d_midpoint1_y_coordinate"] == 0)
                | (res["fugitive_2d_midpoint2_y_coordinate"] == 0)
                | (res["fugitive_2d_midpoint1_x_coordinate"] == 0)
                | (res["fugitive_2d_midpoint2_x_coordinate"] == 0)
            )
            & res["emission_release_point_type"].isin(erp_types)
        ]
        self.qa_df = res
        return len(res.index)
