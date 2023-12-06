from modules.queries.QA.qa_base import QABase
from modules.utils import Join, get_static, calc_agg

"""
'QA 15 - Unscreened POMs: this QA will check if there are emissions of POM(s) that cannot be screened

'qry_QA_15_UnscreenedPOMs - returns records of POM(s) that cannot be screened
"""


class UnscreenedPOMs(QABase):
    qa_num = "15"
    qa_title = "Unscreened POMs"

    def run(self):
        num_records = self.qry_QA_15_UnscreenedPOMs()
        if num_records == 0:
            self.update(
                "Informational",
                "All emissions of POMs, if present, can be screened for multipathway effects.",
                "None.",
            )
        else:
            self.update(
                "Warning",
                f"""
                Emissions of one or more POM congeners cannot be properly screened for multipathway impacts 
                because they have not been evaluated for oral toxicity and environmental fate-and-transport characteristics. 
                The multipathway screen will ignore these POM congeners unless EPA directs us how to proceed. 
                See information in the "15" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_15_UnscreenedPOMs",
            )
        return self

    def qry_QA_15_UnscreenedPOMs(self):
        group_by = [
            "hap_category_name",
            "pollutant_description",
            "pollutant_code",
            "sppd_facility_identifier",
            "shortpb-hap/ecohapname",
            "chem name for tier 2 tool",
        ]
        order_by = [
            "hap_category_name",
            "pollutant_description",
            "pollutant_code",
            "Total actual_emissions_tpy",
            "sppd_facility_identifier",
        ]
        static_static_pollutantCrosswalk = get_static(
            "static_PollutantCrosswalk_andMetalSpeciations"
        )
        res = Join().join(
            left=self.df, right=static_static_pollutantCrosswalk, on="pollutant_code"
        )

        res = res.loc[
            (res["shortpb-hap/ecohapname"] == "POM")
            & (
                (res["chem name for tier 2 tool"] == "")
                | (res["chem name for tier 2 tool"].isna())
            )
        ]

        res = calc_agg(
            res,
            group_by,
            "sum",
            "actual_emissions_tpy",
            "Total actual_emissions_tpy",
        )
        self.qa_df = res[order_by]
        return len(res.index)
