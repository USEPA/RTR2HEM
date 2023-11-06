from modules.queries.QA.qa_base import QABase

"""
NOTE - NOT IMPLEMENTED
'QA 08 - Fixing Length and Width Parameters for Area and Line Sources: this will set fugitive length and width to 3.28084 (=1 m)
        'if they are less than that.

'qry_QA_08a_LengthWidthFix - if area/line sources are present, this query returns those sources with >0 but <3.28084 data for FUGITIVE_LENGTH_SIGMAX_FT and FUGITIVE_WIDTH_SIGMAY_FT
'qry_QA_08b_LengthWidthFix - if 08a is not an empty table, this query fixes problematic sources by setting such values to 3.28084.
"""


class LengthWidthFix(QABase):
    qa_num = "08"
    qa_title = "Fixing Parameters for Area Sources"

    def run(self):
        self.update(
            "N/A",
            "This QA step is no longer needed and was removed on 07/24/2020.",
            "None.",
        )
        return self
