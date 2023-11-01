from modules.queries.QA.qa_base import QABase
from modules.utils import Join, group, calc_agg

"""
QA 02 - Unique Facilities: this QA ensures that no facility has multiple different address information
"""


class UniqueFacilities(QABase):
    QA_num = "02"
    QA_title = "Unique Facilities"

    def run(self):
        only_unique_locations = self.qry_QA_02d_UniqueFac()

        # no facility with more than one unique location detail
        if only_unique_locations:
            self.update(
                "Passed QA",
                "As expected, each facility has a single, unique set of name and address information.",
                "None.",
            )
        else:
            num_locations = len(self.qry_QA_02c_UniqueFac().index)
            self.update(
                "Fatal Error",
                f"""Number of facilities with inconsistencies in name or address information: 
                {num_locations} (facility defined as field SPPD_FACILITY_IDENTIFIER). 
                This will cause each facility to appear more than once in two of the output files. 
                See information in the ""02"" sheet of the ""RTRtoHEMandTier1_QA"" Excel file output by this QA program. 
                """,
                "qry_QA_02d_UniqueFac",
            )
        return self

    # TODO -- where is this used..?
    def qry_QA_02a_UniqueFac(self):
        """
        list of unique facilities using SPPD_FACILITY_IDENTIFIER
        """
        id = ["sppd_facility_identifier"]
        return group(self.df, id, True)

    def qry_QA_02b_UniqueFac(self):
        """
        list of unique facilities using multiple location fields
        """
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
        return group(self.df, group_by, True)

    def qry_QA_02c_UniqueFac(self):
        """
        this query filters for facilities with more than one unique location details
        """
        group_by = [
            "sppd_facility_identifier",
            "facility_name",
        ]
        res = self.qry_QA_02b_UniqueFac()
        res = calc_agg(res, group_by, "count", "facility_name", "CountOfFACILITY_NAME")
        return res.loc[res["CountOfFACILITY_NAME"] > 1]

    def qry_QA_02d_UniqueFac(self):
        """
        this query joins 02c to 02b by the SPPD_Facility to supply details on those facilities with
        more than one unique location details
        """
        all_unique_facilities = self.qry_QA_02b_UniqueFac()
        multiple_locations = self.qry_QA_02c_UniqueFac()
        res = Join().join(
            [all_unique_facilities, multiple_locations],
            on="sppd_facility_identifier",
        )
        res = res.loc[res["CountOfFACILITY_NAME"] > 1]
        return len(res.index) == 0
