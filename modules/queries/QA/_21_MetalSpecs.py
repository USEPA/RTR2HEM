import pandas as pd
from modules.queries.shared_queries import split_by_reg_codes
from modules.queries.QA.qa_base import QABase
from modules.utils import Join, get_static, calc_agg

"""
'QA 21 - Pollutants with Metal Speciations: this QA will indicate if any of the pollutants in the modeling file will have
'their emissions reduced in the tool's output files for modeling, due to usage of a metal speciation factor.

'qry_QA_21a_MetalSpecs - summation of actual, allowable, and acute emissions within and outside the target source category
'qry_QA_21b_MetalSpecs - this query returns information on the emissions of pollutants within and outside of the target source category with
                        'metal speciation factors that are not equal to 1
"""


class MetalSpecs(QABase):
    qa_num = "21"
    qa_title = "Pollutants with Metal Speciations"

    def run(self):
        num_metal_specs = self.qry_QA_21b_MetalSpecs()
        if num_metal_specs == 0:
            self.update(
                "Informational",
                f"""
                The modeling file did not contain any pollutant with pre-determined metal speciation factors 
                that would have reduced the emitted mass to only the metal component of the compound.
                """,
                "None.",
            )
        else:
            self.update(
                "Informational",
                f"""
                The tool''s processing will multiply the emitted mass of some pollutants 
                by pre-determined metal speciation factors, thus reducing the 
                emitted mass to only the metal component of the compound. 
                The effect of these speciations (reductions in emissions) is shown 
                in the "21" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_21b_MetalSpecs",
            )
        return self

    def qry_QA_21a_MetalSpecs(self):
        out_res, in_res = split_by_reg_codes(self)
        group_by = [
            "regulatory_code",
            "hap_category_name",
            "pollutant_description",
            "pollutant_code",
        ]

        actual_out = calc_agg(out_res, group_by, "sum", "actual_emissions_tpy")
        allowable_out = calc_agg(out_res, group_by, "sum", "allowable_emissions_tpy")
        acute_out = calc_agg(out_res, group_by, "sum", "acute_emissions_tpy")
        out_res = Join().join(
            [actual_out, allowable_out, acute_out],
            on=group_by,
        )

        actual_in = calc_agg(in_res, group_by, "sum", "actual_emissions_tpy")
        allowable_in = calc_agg(in_res, group_by, "sum", "allowable_emissions_tpy")
        acute_in = calc_agg(in_res, group_by, "sum", "acute_emissions_tpy")
        in_res = Join().join(
            [actual_in, allowable_in, acute_in],
            on=group_by,
        )

        return pd.concat([out_res, in_res], ignore_index=True)

    def qry_QA_21b_MetalSpecs(self):
        static_PollutantCrosswalk = get_static(
            "static_PollutantCrosswalk_andMetalSpeciations"
        )
        res = self.qry_QA_21a_MetalSpecs()
        res = Join().join(
            left=res,
            right=static_PollutantCrosswalk,
            on="pollutant_code",
            how="left",
        )
        res = res.loc[res["metal_speciation_factor"] != 1]

        group_by = [
            "hap_category_name",
            "pollutant_description",
            "pollutant_code",
            "hem3_chemical_name",
            "metal_to_speciate_by",
            "metal_speciation_factor",
            "diff_actual",
            "diff_allowable",
            "diff_acute",
        ]
        res["diff_actual"] = (
            res["metal_speciation_factor"] * res["actual_emissions_tpy"]
            - res["actual_emissions_tpy"]
        )
        res["diff_allowable"] = (
            res["metal_speciation_factor"] * res["allowable_emissions_tpy"]
            - res["allowable_emissions_tpy"]
        )
        res["diff_acute"] = (
            res["metal_speciation_factor"] * res["acute_emissions_tpy"]
            - res["acute_emissions_tpy"]
        )

        columns = ["regulatory_code"] + group_by
        res = res[columns].sort_values("regulatory_code")
        self.qa_df = res
        return len(res.index)
