from modules.queries.QA.qa_base import QABase
from modules.utils import group

"""
'QA 10 - Parameters for Volume Sources: this QA will check for appropriate parameters values for volume sources, if present.

'qry_QA_10_VolParams - this query returns unique sources that have unexpected values for volume source parameters
"""


class VolParams(QABase):
    qa_num = "10"
    qa_title = "Parameters for Volume Sources"

    def run(self):
        num_sources_unexpected_vals = self.qry_QA_10_VolParams()
        if num_sources_unexpected_vals == 0:
            self.update(
                "Passed QA",
                """
                All volume sources (if present) have valid parameter values. 
                Evaluated fields include: STACK_HEIGHT (ft) and FUGITIVE_WIDTH_SIGMAY_FT, which must have positive values.
                """,
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                Number of volume sources with unexpected parameter values: {num_sources_unexpected_vals}. 
                These sources cannot be modeled with these unexpected parameter values. 
                Evaluated fields include: STACK_HEIGHT (ft) and FUGITIVE_WIDTH_SIGMAY_FT, which must have positive values. 
                See information in the "10" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_10_VolParams",
            )
        return self

    def qry_QA_10_VolParams(self):
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
            "emission_process_group",
        ]
        erp_types = ["7"]
        res = group(self.df, group_by, True)
        res = res.loc[
            ((res["stack_height (ft)"] <= 0) | (res["fugitive_width_sigmay_ft"] <= 0))
            & res["emission_release_point_type"].isin(erp_types)
        ]
        self.qa_df = res
        return len(res.index)
