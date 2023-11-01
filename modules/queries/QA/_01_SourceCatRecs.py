from modules.queries.QA.qa_base import QABase
from modules.utils import group, config

"""
'QA 01 - Facilities Without Source Category Recrods: this QA checks that each facility in a modeling file has
'at least 1 record that belongs to the source category, though it's possible (but infrequent) for this not to be the case.
"""


# NOTE: if cat only, this step gets skipped... and all regulatory codes get set as inside category?
class SourceCatRecs(QABase):
    QA_num = "01"
    QA_title = "Facilities Without Records in the Source Category"

    def run(self):
        if config.only_category:
            self.update(
                "QA Not Needed",
                "You have indicated that all records in this RTR modeling file are within the category.",
                "None.",
            )
        elif not 1 in config.reg_codes.values():  # no codes selected
            self.update(
                "QA Not Needed",
                "You have indicated that all records in this RTR modeling file are not within the category.",
                "None.",
            )
        else:  # at least 1 code selected, but n>0 records do not have any facilities with selected codes
            records = self.missing_records()
            if len(records) == 0:
                self.update(
                    "Passed QA",
                    "All facilities have records in the target source category.",
                    "None.",
                )
            else:
                self.update(
                    "Warning",
                    f"""Number of facilities with no records in the target source category: 
                                {len(records)} (facility defined as field SPPD_FACILITY_IDENTIFIER). 
                                See information in the "01" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program. 
                                Contact EPA to inquire about this.""",
                    "qry_QA_01c_SrcCatRecs",  # TODO update,
                )
        return self

    def missing_records(self):
        # this query identifies all unique facility IDs that
        # have no records within the target source category
        reg_codes = [k for k, v in config.reg_codes.items() if v == 1]

        res = group(self.df, ["sppd_facility_identifier", "regulatory_code"])
        records_in_category = res.loc[res["regulatory_code"].isin(reg_codes)]
        records_in_category = set(records_in_category["sppd_facility_identifier"])

        all_records = group(self.df, ["sppd_facility_identifier"])
        all_records = set(all_records["sppd_facility_identifier"])

        return list(all_records - records_in_category)
