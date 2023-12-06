from modules.queries.QA.qa_base import QABase
from modules.utils import group

"""
'QA 07 - Parameters for Point Sources: this QA will check for appropriate parameters values for point sources, if present.

'qry_QA_07_PointParams - this query returns unique sources that have unexpected values for point source parameters
"""


class PointParams(QABase):
    qa_num = "07"
    qa_title = "Parameters for Point Sources"

    def run(self):
        num_sources_unexpected_vals = self.qry_QA_07_PointParams()
        if num_sources_unexpected_vals == 0:
            self.update(
                "Passed QA",
                """
                All point sources (if present) have valid parameter values. 
                Evaluated fields include: STACK_HEIGHT (ft), EXIT_GAS_TEMPERATURE (F), 
                STACK_DIAMETER (ft), and EXIT_GAS_VELOCITY (ft/sec), 
                which must have positive values, and FUGITIVE_LENGTH_SIGMAX_FT, FUGITIVE_WIDTH_SIGMAY_FT, 
                and FUGITIVE_ANGLE_DEGREES, which must be 0 or Null.
                """,
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                Number of point sources with unexpected parameter values: {num_sources_unexpected_vals}. 
                These sources cannot be modeled with these unexpected parameter values. 
                Evaluated fields include: STACK_HEIGHT (ft), EXIT_GAS_TEMPERATURE (F), 
                STACK_DIAMETER (ft), and EXIT_GAS_VELOCITY (ft/sec), 
                which must have positive values, and FUGITIVE_LENGTH_SIGMAX_FT, FUGITIVE_WITDH_SIGMAY_FT, 
                and FUGITIVE_ANGLE_DEGREES, which must be 0 or Null. 
                See information in the "07" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_07_PointParams",
            )
        return self

    def qry_QA_07_PointParams(self):
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
            "emission_process_group",
        ]
        erp_types = ["2", "3", "4", "5", "6", "8", "99"]
        res = group(self.df, group_by, True)
        res = res.loc[
            (
                (res["fugitive_length_sigmax_ft"] > 0)
                | (res["fugitive_width_sigmay_ft"] > 0)
                | (res["fugitive_angle_degrees"] > 0)
                | (res["stack_height (ft)"] <= 0)
                | (res["exit_gas_temperature (f)"] <= 0)
                | (res["stack_diameter (ft)"] <= 0)
                | (res["exit_gas_velocity (ft/sec)"] <= 0)
            )
            & res["emission_release_point_type"].isin(erp_types)
        ]
        self.qa_df = res
        return len(res.index)
