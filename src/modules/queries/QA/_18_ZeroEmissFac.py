from src.modules.queries.QA.qa_base import QABase
from src.utils import Join, get_static, calc_agg, group

"""
'QA 18 - Facilities with zero emissions: This QA will present those facilities with zero emissions for every source totals from the modeling file.

'qry_QA_18_ZeroEmissFac - this query returns the facilities with zero actual emissions.
"""


class ZeroEmissFac(QABase):
    qa_num = "18"
    qa_title = "Zero-emission Facilities"

    def run(self):
        num_facil_zero_emiss = self.qry_QA_18_ZeroEmissFac()
        if num_facil_zero_emiss == 0:
            self.update(
                "Informational",
                f"All facilities have at least one source with emissions > 0.",
                "None.",
            )
        else:
            self.update(
                "Informational",
                f"""
                Number of facilities with zero actual emissions: {num_facil_zero_emiss}. These facilities have zero actual emissions for all source IDs. 
                See information in the "18" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_18_ZeroEmissFac",
            )
        return self

    def qry_QA_18_ZeroEmissFac(self):
        group_by = ["sppd_facility_identifier"]
        actual_res = calc_agg(self.df, group_by, "sum", "actual_emissions_tpy")
        allowable_res = calc_agg(self.df, group_by, "sum", "allowable_emissions_tpy")
        acute_res = calc_agg(self.df, group_by, "sum", "acute_emissions_tpy")

        res = Join().join(
            [actual_res, allowable_res, acute_res],
            on="sppd_facility_identifier",
        )
        res = res.loc[res["actual_emissions_tpy"] == 0]
        self.qa_df = res
        return len(res.index)
