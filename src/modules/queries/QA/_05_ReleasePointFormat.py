from src.modules.queries.QA.qa_base import QABase
from src.utils import group, config

"""
QA 05 - Release Point Format: this QA check will repair (if needed) the formats of the field EMISSION_RELEASE_POINT_TYPE - must not have leading 0's.

qry_QA_05a_ReleasePointFormat - this query returns information on sources where EMISSION_RELEASE_POINT_TYPE values have leading 0's
qry_QA_05b_ReleasePointFormat - this query returns the number of sources whose release point types have leading 0's
qry_QA_05c_ReleasePointFormat - this query updates EMISSION_RELEASE_POINT_TYPE records in the data base by removing leading 0's
"""


class ReleasePointFormat(QABase):
    qa_num = "05"
    qa_title = "Format of Release Point"

    def run(self):
        num_rpf_incorrect_format = self.qry_QA_05b_ReleasePointFormat()
        if num_rpf_incorrect_format == 0:
            self.update(
                "Repairs Not Needed",
                "All records use the correct format for the field EMISSION_RELEASE_POINT_TYPE.",
                "None.",
            )
        else:
            self.update(
                "Repairs Were Needed",
                f"""
                Number of sources with incorrectly formatted release point types: {num_rpf_incorrect_format} 
                (the field EMISSION_RELEASE_POINT_TYPE must not have leading 0''s).
                This tool has repaired the formats for proper processing.
                See information in the "05" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_05a_ReleasePointFormat",
            )
            self.qry_QA_05c_ReleasePointFormat()
        return self

    def qry_QA_05a_ReleasePointFormat(self):
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
        res = group(self.df, group_by, True)
        res = res.loc[res["emission_release_point_type"].str[0] == "0"]
        self.qa_df = res
        return res

    def qry_QA_05b_ReleasePointFormat(self):
        group_by = [
            "sppd_facility_identifier",
            "emission_unit_id",
            "process_id",
            "emission_release_point_id",
        ]
        res = self.qry_QA_05a_ReleasePointFormat()
        res = group(res, group_by, True)
        return len(res.index)

    def qry_QA_05c_ReleasePointFormat(self):
        erp_type = "emission_release_point_type"
        new_vals = []
        for val in config.input_df[erp_type]:
            if val[0] == "0" and len(val) > 1:
                new_vals.append(val[1:])
            else:
                new_vals.append(val)
        config.input_df[erp_type] = new_vals
