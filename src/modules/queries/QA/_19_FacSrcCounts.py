import pandas as pd
from src.modules.queries.shared_queries import split_by_reg_codes
from src.modules.queries.QA.qa_base import QABase
from src.utils import calc_agg, group

"""
'QA 19 - Facility and Source Counts: this QA will present the counts of facilities facilities (field SPPD_FACILITY_IDENTIFIER) and
'sources (unique combination of fields SPPD_FACILITY_IDENTIFIER, EMISSION_UNIT_ID, PROCESS_ID, and EMISSION_RELEASE_POINT_ID) from the modeling file.

The logic for these queries has been combined into qry_QA_19_EmissTots
'qry_QA_19a_FacSrcCounts - this query indicates which facilities are inside or outside of the target source category
'qry_QA_19b_FacSrcCounts - this query counts number of facilities inside or outside of the target source category
'qry_QA_19c_FacSrcCounts - this query indicates which sources are inside or outside of the target source category
'qry_QA_19d_FacSrcCounts - this query counts number of sources inside or outside of the target source category
'qry_QA_19e_FacSrcCounts - this query returns the number of facilities and the number of sources within the source category and within the modeling
                          'file in total
"""


class FacSrcCounts(QABase):
    qa_num = "19"
    qa_title = "Facility and Source Counts"

    def run(self):
        self.qry_QA_19_EmissTots()
        self.update(
            "Informational",
            f"""
            The counts of facilities and sources, within and outside the target source category, 
            are shown in the "19" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
            """,
            "qry_QA_19_EmissTots",
        )
        return self

    def qry_QA_19_EmissTots(self):
        out_res, in_res = split_by_reg_codes(self)

        # number of facilities
        group_by = ["sppd_facility_identifier"]
        out_num_facil = group(out_res, group_by, True)
        in_num_facil = group(in_res, group_by, True)

        # number of sources
        group_by = [
            "sppd_facility_identifier",
            "emission_unit_id",
            "process_id",
            "emission_release_point_id",
        ]
        out_sources = group(out_res, group_by, True)
        in_sources = group(in_res, group_by, True)

        out_data = [
            "OUTSIDE SOURCE CATEGORY",
            calc_agg(out_num_facil, [], "count", "sppd_facility_identifier"),
            calc_agg(out_sources, [], "count", "sppd_facility_identifier"),
        ]
        in_data = [
            "WITHIN SOURCE CATEGORY",
            calc_agg(in_num_facil, [], "count", "sppd_facility_identifier"),
            calc_agg(in_sources, [], "count", "sppd_facility_identifier"),
        ]
        total_data = [
            "TOTAL",
            out_data[1] + in_data[1],
            out_data[2] + in_data[2],
        ]

        self.qa_df = pd.DataFrame(data=[out_data, in_data, total_data])
