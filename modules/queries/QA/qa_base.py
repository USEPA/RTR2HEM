from modules.utils import config


class QABase:
    QA_num = "NONE"
    QA_title = "NONE"
    QA_out = "NONE"
    QA_msg = "NONE"
    QA_result = "NONE"

    def __init__(self):
        self.df = config.input_df

    def update(self, out, msg, result):
        self.QA_out = out
        self.QA_msg = msg
        self.QA_result = result

    def get(self):
        return {
            "QA_Number": self.QA_num,
            "QA_Title": self.QA_title,
            "QA_Outcome": self.QA_out,
            "QA_Message": self.QA_msg,
            "QA_Result": self.QA_result,
        }
