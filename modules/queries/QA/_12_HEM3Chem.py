from modules.queries.QA.qa_base import QABase
from modules.utils import Join, get_static, vset, calc_agg

"""
'QA 12 - Pollutants that Cannot be Modeled for Risk/Hazard: this QA will check to make sure pollutants are recognized.

'qry_QA_12a_HEM3Chem - returns pollutants with a join fail (pollutant_code non-existent in the "static_PollutantCrosswalk..." table) or a blank HEM3_CHEMICAL_NAME
'qry_QA_12b_HEM3Chem - returns qry_QA_12a_HEM3Chem with Yes/No in the "IN CROSSWALK?" column

combined 12a and 12b into qry_QA_12_HEM3Chem
Pollutants that cannot be assessed: they are not recognized (“No” for the field IN CROSSWALK?) 
    and/or they are not in the RTR dose-response library (“Yes” for the field IN CROSSWALK? and blank for the field HEM3_CHEMICAL_NAME).
"""


class HEM3Chem(QABase):
    qa_num = "12"
    qa_title = "Pollutants that Cannot be Modeled for Inhalation Risk/Hazard"

    def run(self):
        num_invalid_pollutants = self.qry_QA_12_HEM3Chem()
        if num_invalid_pollutants == 0:
            self.update(
                "Passed QA",
                """
                All pollutants are in the dose-response library and can be modeled for inhalation risks or hazards.
                """,
                "None.",
            )
        else:
            self.update(
                "Fatal Error",
                f"""
                One or more pollutant(s) cannot be modeled for inhalation risks 
                or hazards because they cannot be recognized and/or they are not currently in the RTR dose-response library. 
                These emissions cannot be properly included with the modeling. 
                See information in the "12" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program, 
                where unrecognized pollutants are indicated with "No" in the field IN CROSSWALK? in that sheet, 
                and pollutants not in the dose-response library are indicated 
                with "Yes" in the field IN CROSSWALK? and a blank value in the field HEM3_CHEMICAL_NAME.
                """,
                "qry_QA_12b_HEM3Chem",
            )
        return self

    def qry_QA_12_HEM3Chem(self):
        group_by = [
            "hap_category_name",
            "pollutant_description",
            "pollutant_code",
            "in_crosswalk",
            "hem3_chemical_name",
            "cas number",
            "pb-hap/ecohap",
            "sppd_facility_identifier",
        ]
        static_pollutantCrosswalk = get_static(
            "static_PollutantCrosswalk_andMetalSpeciations"
        )
        static_pollutantCrosswalk = static_pollutantCrosswalk.rename(
            columns={"pollutant_code": "pollutant_code_static"}
        )

        res = Join().join(
            left=self.df,
            right=static_pollutantCrosswalk,
            left_on="pollutant_code",
            right_on="pollutant_code_static",
            how="left",
        )
        res = res.loc[
            res["pollutant_code_static"].isnull() | (res["hem3_chemical_name"] == "")
        ].fillna("")

        vset(res, "in_crosswalk", self.pollutant_code_exists, ["pollutant_code_static"])
        res = calc_agg(res, group_by, "sum", "actual_emissions_tpy")

        col_order = [
            "hap_category_name",
            "pollutant_description",
            "pollutant_code",
            "in_crosswalk",
            "hem3_chemical_name",
            "cas number",
            "pb-hap/ecohap",
            "actual_emissions_tpy",
            "sppd_facility_identifier",
        ]
        res = res[col_order]
        self.qa_df = res
        return len(res.index)

    def pollutant_code_exists(self, poll_code):
        if poll_code:
            return "Yes"
        return "No"
