from src.modules.queries.QA.qa_base import QABase
from src.utils import calc_agg

"""
'QA 13 - Speciated Chromium and Mercury: this QA will check if there are emissions of generic/unspeciated mercury and/or chromium.

'qry_QA_13_GenericHgCr - returns records of generic/unspeciated mercury and/or chromium
"""


class GenericHgCr(QABase):
    qa_num = "13"
    qa_title = "Speciated Chromium and Mercury"

    def run(self):
        num_records = self.qry_QA_13_GenericHgCr()
        if num_records == 0:
            self.update(
                "Passed QA",
                "All emissions of chromium and mercury, if present, are properly speciated. ",
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                One or more pollutants should not be modeled as-is because they are generic/unspeciated mercury or chromium. 
                These emissions cannot be properly included with the modeling. 
                See information in the "13" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_13_GenericHgCr",
            )
        return self

    def qry_QA_13_GenericHgCr(self):
        pollutant_codes = [
            "136",
            "199",
            "7439976",
            "7440473",
        ]
        group_by = [
            "hap_category_name",
            "pollutant_description",
            "pollutant_code",
            "sppd_facility_identifier",
        ]
        order_by = [
            "hap_category_name",
            "pollutant_description",
            "pollutant_code",
            "Total actual_emissions_tpy",
            "sppd_facility_identifier",
        ]

        res = self.df.loc[self.df["pollutant_code"].isin(pollutant_codes)]
        res = calc_agg(
            res,
            group_by,
            "sum",
            "actual_emissions_tpy",
            "Total actual_emissions_tpy",
        )
        self.qa_df = res[order_by]
        return len(res.index)
