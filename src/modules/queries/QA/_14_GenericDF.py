from src.modules.queries.QA.qa_base import QABase
from src.utils import calc_agg

"""
'QA 14 - Speciated Dioxins/Furans: this QA will check if there are emissions of generic/unspeciated dioxins/furans.

'qry_QA_14_GenericDF - returns records of generic/unspeciated dioxins/furans
"""


class GenericDF(QABase):
    qa_num = "14"
    qa_title = "Speciated Dioxins/Furans"

    def run(self):
        num_records = self.qry_QA_14_GenericDF()
        if num_records == 0:
            self.update(
                "Passed QA",
                "All emissions of dioxins/furans, if present, are properly speciated.",
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                One or more pollutants should not be modeled as-is because they are generic/unspeciated dioxins/furans. 
                These emissions cannot be properly included with the modeling. 
                See information in the "14" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_14_GenericDF",
            )
        return self

    def qry_QA_14_GenericDF(self):
        pollutant_codes = [
            "136677093",
            "136677106",
            "155",
            "262124",
            "30402143",
            "30402154",
            "34465468",
            "36088229",
            "37871004",
            "38998753",
            "41903575",
            "55684941",
            "622",
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
