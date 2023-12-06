from modules.queries.QA.qa_base import QABase
from modules.utils import Join, get_static, calc_agg, group

"""
'QA 16 - Source Types Present: this QA will identify which types of emission sources are in the modeling file.

'qry_QA_16a_SrcTypes - this query returns information on the types of emission sources in the modeling file
'qry_QA_16b_SrcTypes - this query returns the types of emission sources that exist in the modeling file and the number of sources that exist for each type

"""


class SrcTypes(QABase):
    qa_num = "16"
    qa_title = "Source Types Present"

    def run(self):
        self.qry_QA_16b_SrcTypes()
        self.update(
            "Informational",
            f"""
            The types of sources present in the modeling file are shown in the "16" sheet of the 
            "RTRtoHEMandTier1_QA" Excel file output by this QA program.
            """,
            "qry_QA_16b_SrcTypes",
        )
        return self

    def qry_QA_16a_SrcTypes(self):
        group_by = [
            "aermod source type",  # modeled source type
            "emission_release_point_type",
            "description",  # description of emission_release_point_type
            "sppd_facility_identifier",
            "process_id",
            "emission_unit_id",
            "emission_release_point_id",
        ]
        static_erpts = get_static("static_ERPTs")
        res = Join().join(
            left=self.df,
            right=static_erpts,
            how="left",
            on="emission_release_point_type",
        )

        res.loc[
            (res["aermod source type"].isna()) | (res["description"].isna()),
            ["aermod source type", "description"],
        ] = "UNRECOGNIZED RELEASE POINT TYPE"

        res = group(res, group_by, True).sort_values(group_by)
        return res

    def qry_QA_16b_SrcTypes(self):
        res = self.qry_QA_16a_SrcTypes()
        columns = [
            "aermod source type",
            "emission_release_point_type",
            "description",
            "sppd_facility_identifier",
        ]
        group_by = [
            "aermod source type",
            "emission_release_point_type",
            "description",
        ]
        res = calc_agg(res, group_by, "count", "sppd_facility_identifier")
        self.qa_df = res[columns].sort_values("emission_release_point_type")
