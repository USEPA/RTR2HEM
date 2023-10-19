from modules.queries.QA import QABase
from modules.utils import Join, group, calc_agg

"""
QA 03 - Unique Sources: this QA ensures that no emission source has multiple different stack parameters
        Calls QA04Hemispheres

NOTE -- not implemented yet!
'qry_QA_03a_UniqueSrc - this query returns a list of unique emission sources in the input_EmissionInventory_withICFWork
                        'table using the SPPD_FACILITY_IDENTIFIER & PROCESS_ID & EMISSION_UNIT_ID & EMISSION_RELEASE_POINT_ID

'qry_QA_03b_UniqueSrc - this query returns a list of unique emission sources in the input_EmissionInventory_withICFWork
                        'table and other source parameter fields

'qry_QA_03c_UniqueSrc - this query joins 03a to 03b by the SPPD_FACILITY_IDENTIFIER & PROCESS_ID & EMISSION_UNIT_ID & EMISSION_RELEASE_POINT_ID
                        'fields and filters for facilities with more than one unique emission source detail to supply details on those facilities
                        'with more than one set of stack parameters

'qry_QA_03d_UniqueSrc - this query joins 03c to 03b by the SPPD_FACILITY_IDENTIFIER & PROCESS_ID & EMISSION_UNIT_ID & EMISSION_RELEASE_POINT_ID
                        'fields to supply details on those facilities with more than one set of stack parameters
"""


class UniqueSources(QABase):
    QA_num = "03"
    QA_title = "Unique Sources"

    def run(self):
        only_unique_emissions = self.qry_QA_03d_UniqueSrc()

        # no emission source with more than one unique emission source data
        if only_unique_emissions:
            self.update(
                "Passed QA",
                "As expected, each source has a single, unique set of source parameters.",
                "None.",
            )
        else:
            num_emissions = len(self.qry_QA_03c_UniqueSrc().index)
            self.update(
                "Fatal Error",
                f"""Number of sources with inconsistencies in source parameters: 
                {num_emissions} (source defined as combination of fields SPPD_FACILITY_IDENTIFIER, EMISSION_UNIT_ID, 
                PROCESS_ID, and EMISSION_RELEASE_POINT_ID). 
                This will cause each such source to be modeled as more than one source. 
                See information in the ""03"" sheet of the ""RTRtoHEMandTier1_QA"" Excel file output by this QA program. 
                """,
                "qry_QA_03d_UniqueSrc",
            )
        return self.get()

    def qry_QA_03b_UniqueSrc(self):
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
        return group(self.df, group_by, True)

    def qry_QA_03c_UniqueSrc(self):
        group_by = [
            "sppd_facility_identifier",
            "emission_unit_id",
            "process_id",
            "emission_release_point_id",
            "emission_release_point_type",
        ]
        res = self.qry_QA_03b_UniqueSrc()
        res = calc_agg(
            res,
            group_by,
            "count",
            "emission_release_point_type",
            "CountOfEMISSION_RELEASE_POINT_TYPE",
        )
        return res.loc[res["CountOfEMISSION_RELEASE_POINT_TYPE"] > 1]

    def qry_QA_03d_UniqueSrc(self):
        """
        SELECT qry_QA_03b_UniqueSrc.*
        FROM qry_QA_03c_UniqueSrc INNER JOIN qry_QA_03b_UniqueSrc ON
        (qry_QA_03c_UniqueSrc.EMISSION_RELEASE_POINT_ID = qry_QA_03b_UniqueSrc.EMISSION_RELEASE_POINT_ID)
        AND (qry_QA_03c_UniqueSrc.PROCESS_ID = qry_QA_03b_UniqueSrc.PROCESS_ID)
        AND (qry_QA_03c_UniqueSrc.EMISSION_UNIT_ID = qry_QA_03b_UniqueSrc.EMISSION_UNIT_ID)
        AND (qry_QA_03c_UniqueSrc.SPPD_FACILITY_IDENTIFIER = qry_QA_03b_UniqueSrc.SPPD_FACILITY_IDENTIFIER);

        """
        all_unique_emissions = self.qry_QA_03b_UniqueSrc()
        multiple_emissions = self.qry_QA_03c_UniqueSrc()
        res = Join().join(
            [all_unique_emissions, multiple_emissions],
            on=[
                "emission_release_point_id",
                "process_id",
                "emission_unit_id",
                "sppd_facility_identifier",
            ],
        )
        res = res.loc[res["CountOfEMISSION_RELEASE_POINT_TYPE"] > 1]
        return len(res.index) == 0
