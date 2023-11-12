import pandas as pd
from modules.utils import config


class QABase:
    qa_num = "NOT SET"
    qa_title = "NOT SET"
    qa_out = "NOT SET"
    qa_msg = "NOT SET"
    qa_result = "NOT SET"

    qa_df: pd.DataFrame = None

    filename = f"RTRtoHEMandTier1_QA"
    template_name = "Tier1_QA_Details"
    sheet_name = "NOT SET"

    rowstart = 4
    colstart = 1

    color_map = {
        "#758c48": ["Passed QA"],  # green
        "#ffc20e": ["Warning", "Repairs Were Needed"],  # yellow
        "#ba1419": ["Fatal Error"],  # red
        "#807b90": ["QA Not Needed", "Repairs Not Needed", "Informational"],  # grey
        "#000000": ["N/A"],  # black
    }

    def __init__(self):
        self.df = config.input_df
        self.filename = f"{config.src_cat_name}_RTRtoHEMandTier1_QA_{config.timestamp}"
        self.qa_df = pd.DataFrame()
        self.run()

    # override
    def run(self):
        return self

    def update(self, out, msg, result):
        self.qa_out = out
        self.qa_msg = msg
        self.qa_result = result
        self.sheet_name = self.qa_num

    def get(self):
        return {
            "QA_Number": self.qa_num,
            "QA_Title": self.qa_title,
            "QA_Outcome": self.qa_out,
            "QA_Message": self.qa_msg,
            "QA_Result": self.qa_result,
        }
