from modules.queries.QA.qa_base import QABase
from modules.utils import Join, group, get_static, config

"""
'QA 06 - Release Point Type: this QA check will return sources with invalid values for the field EMISSION_RELEASE_POINT_TYPE.
'Current valid values are 1-10 and 99

'qry_QA_06a_ReleasePointType - this query returns unique facilities that have unexpected values for the EMISSION_RELEASE_POINT_TYPE field
'qry_QA_06b_ReleasePointType - this query returns unique sources that have unexpected values for the EMISSION_RELEASE_POINT_TYPE field
"""


class ReleasePointType(QABase):
    qa_num = "06"
    qa_title = "Release Point Type"

    def run(self):
        num_facil_unexpected_vals = self.qry_QA_06b_ReleasePointType()
        if num_facil_unexpected_vals == 0:
            self.update(
                "Passed QA",
                "All sources have valid values for the field EMISSION_RELEASE_POINT_TYPE.",
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                "Number of sources with unexpected values for the field EMISSION_RELEASE_POINT_TYPE: {num_facil_unexpected_vals}. 
                These sources cannot be modeled.
                See information in the "06" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_06a_ReleasePointType",
            )
        return self

    def qry_QA_06a_ReleasePointType(self):
        group_by = [
            "sppd_facility_identifier",
            "emission_unit_id",
            "process_id",
            "emission_release_point_id",
            "emission_release_point_type",
            "regulatory_code",
            "stack_height (ft)",
            "exit_gas_temperature (f)",
            "stack_diameter (ft)",
            "exit_gas_velocity (ft/sec)",
            "exit_gas_flow_rate (cu ft/sec)",
            "fugitive_length_sigmax_ft",
            "fugitive_width_sigmay_ft",
            "fugitive_angle_degrees",
            "y_coordinate",
            "x_coordinate",
            "fugitive_2d_midpoint1_y_coordinate",
            "fugitive_2d_midpoint2_y_coordinate",
            "fugitive_2d_midpoint1_x_coordinate",
            "fugitive_2d_midpoint2_x_coordinate",
            "emission_process_group",
        ]

        erpts_df = get_static("static_ERPTs")
        res = Join().join(
            left=erpts_df,
            right=config.input_df,
            how="right",
            on="emission_release_point_type",
        )
        res = group(res, group_by, True)
        res = res.loc[res["emission_release_point_type"] == ""]
        self.qa_df = res
        return res

    def qry_QA_06b_ReleasePointType(self):
        group_by = [
            "sppd_facility_identifier",
            "emission_unit_id",
            "process_id",
            "emission_release_point_id",
        ]
        res = self.qry_QA_06a_ReleasePointType()
        res = group(res, group_by, True)
        return len(res.index)
