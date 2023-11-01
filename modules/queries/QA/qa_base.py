from modules.utils import config


class QABase:
    QA_num = "NOT SET"
    QA_title = "NOT SET"
    QA_out = "NOT SET"
    QA_msg = "NOT SET"
    QA_result = "NOT SET"

    filename = "Tier1_QA_Details"
    template_name = "Tier1_QA_Details"
    sheet_name = "NOT SET"

    rowstart = 4
    colstart = 1

    def __init__(self):
        self.df = config.input_df
        self.run()

    # override
    def run(self):
        pass

    def update(self, out, msg, result):
        self.QA_out = out
        self.QA_msg = msg
        self.QA_result = result
        self.sheet_name = self.QA_num

    def get(self):
        return {
            "QA_Number": self.QA_num,
            "QA_Title": self.QA_title,
            "QA_Outcome": self.QA_out,
            "QA_Message": self.QA_msg,
            "QA_Result": self.QA_result,
        }
