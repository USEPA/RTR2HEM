import pandas as pd
from modules.queries.shared_queries import split_by_reg_codes
from modules.queries.QA.qa_base import QABase
from modules.utils import calc_agg

"""
'QA 17 - Emission Totals: This QA will present the emission totals from the modeling file.

'qry_QA_17_EmissTots - this query returns the total actual, allowable, and acute emissions within the source category and within the modeling file in total.
"""


class EmissTots(QABase):
    qa_num = "17"
    qa_title = "Emission Totals"

    def run(self):
        self.qry_QA_17_EmissTots()
        self.update(
            "Informational",
            f"""
            The emission totals, within and outside the target source category, 
            are shown in the "17" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
            """,
            "qry_QA_17_EmissTots",
        )
        return self

    def qry_QA_17_EmissTots(self):
        out_res, in_res = split_by_reg_codes(self)
        out_data = [
            "OUTSIDE SOURCE CATEGORY",
            calc_agg(out_res, [], "sum", "actual_emissions_tpy"),
            calc_agg(out_res, [], "sum", "allowable_emissions_tpy"),
            calc_agg(out_res, [], "sum", "acute_emissions_tpy"),
        ]
        in_data = [
            "WITHIN SOURCE CATEGORY",
            calc_agg(in_res, [], "sum", "actual_emissions_tpy"),
            calc_agg(in_res, [], "sum", "allowable_emissions_tpy"),
            calc_agg(in_res, [], "sum", "acute_emissions_tpy"),
        ]
        total_data = [
            "TOTAL",
            out_data[1] + in_data[1],
            out_data[2] + in_data[2],
            out_data[3] + in_data[3],
        ]

        self.qa_df = pd.DataFrame(data=[out_data, in_data, total_data])
