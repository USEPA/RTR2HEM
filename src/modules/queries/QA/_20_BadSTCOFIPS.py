from src.modules.queries.QA.qa_base import QABase
from src.utils import group

"""
'QA 20 - Facilities With Missing or Suspicious State-County FIPS Codes: this QA will indicate if a record's state-county FIPS
'is missing or is not the expected 5-characters in length.
'This isn't technically a problem, but it means that the facility ID for inhalalation modeling
'will not be constructed as expected (i.e., 5-character FIPS plus the SPPD facility identifier).

'qry_QA_20_BadSTCOFIPS - this query detects any facilities that have records either missing their state-county FIPS
'                        or with their FIPS not as the expected 5 characters.
"""


class BadSTCOFIPS(QABase):
    qa_num = "20"
    qa_title = "Missing or Suspicious State-county FIPS Codes"

    def run(self):
        num_bad_results = self.qry_QA_20_BadSTCOFIPS()
        if num_bad_results == 0:
            self.update(
                "Informational",
                f"All contents of the field STATE_COUNTY_FIPS are the expected five characters in length.",
                "none.",
            )
        else:
            self.update(
                "Warning",
                f"""
                One or more records have state-county FIPS codes that are not the expected five characters in length. 
                This means that the facility IDs created by this tool for modeling will not be constructed as expected 
                (i.e., five-character FIPS plus the SPPD Facility Identifier), but rather will be 
                whatever is in the STATE_COUNTY_FIPS field (whatever its length) plus the SPPD Facility Identifier. 
                The facilities affected by this are shown in the "20" sheet of the "RTRtoHEMandTier1_QA" Excel file output by this QA program.
                """,
                "qry_QA_20_BadSTCOFIPS",
            )
        return self

    def qry_QA_20_BadSTCOFIPS(self):
        group_by = [
            "sppd_facility_identifier",
            "facility_name",
            "location_address",
            "city",
            "county_name",
            "state_county_fips",
            "state_abbr",
            "zipcode",
        ]
        res = group(self.df, group_by, True)
        res = res.loc[res["state_county_fips"].str.len() != 5]
        self.qa_df = res["sppd_facility_identifier"]
        return len(res.index)
