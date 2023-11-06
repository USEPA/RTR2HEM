from modules.queries.QA.qa_base import QABase
from modules.utils import group

"""
'QA 09 - Parameters for Area Sources: this QA will check for appropriate parameters values for area sources, if present.

'qry_QA_09_AreaParamsVal - this query returns unique area sources that have unexpected values for area source parameters
"""


class AreaParamsVal(QABase):
    qa_num = "09"
    qa_title = "Parameters for Area Sources"

    def run(self):
        num_sources_unexpected_vals = self.qry_QA_09_AreaParamsVal()
        if num_sources_unexpected_vals == 0:
            self.update(
                "Passed QA",
                """
                All area sources (if present) have valid parameter values. 
                Evaluated fields include: FUGITIVE_LENGTH_SIGMAX_FT and FUGITIVE_WIDTH_SIGMAY_FT, which must have positive values, 
                and FUGITIVE_ANGLE_DEGREES, which must have values 0-90 inclusive.
                """,
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                Number of area sources with unexpected parameter values: {num_sources_unexpected_vals}. 
                These sources cannot be modeled with these unexpected parameter values. 
                Evaluated fields include: FUGITIVE_LENGTH_SIGMAX_FT and FUGITIVE_WIDTH_SIGMAY_FT, which must have positive values, 
                and FUGITIVE_ANGLE_DEGREES, which must have values 0 to 90 inclusive. 
                See information in the ""09"" sheet of the ""RTRtoHEMandTier1_QA"" Excel file output by this QA program.
                """,
                "qry_QA_09_AreaParamsVal",
            )
        return self

    def qry_QA_09_AreaParamsVal(self):
        group_by = [
            "sppd_facility_identifier",
            "emission_unit_id",
            "process_id",
            "emission_release_point_id",
            "emission_release_point_type",
            "regulatory_code",
            "fugitive_length_sigmax_ft",
            "fugitive_width_sigmay_ft",
            "fugitive_angle_degrees",
            "emission_process_group",
        ]
        erp_types = ["1"]
        res = group(self.df, group_by, True)
        res = res.loc[
            (
                (res["fugitive_length_sigmax_ft"] <= 0)
                | (res["fugitive_width_sigmay_ft"] <= 0)
                | (res["fugitive_angle_degrees"] < 0)
                | (res["fugitive_angle_degrees"] > 90)
            )
            & res["emission_release_point_type"].isin(erp_types)
        ]
        self.qa_df = res
        return len(res.index)
