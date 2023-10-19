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
            "num": self.QA_num,
            "title": self.QA_title,
            "out": self.QA_out,
            "msg": self.QA_msg,
            "result": self.QA_result,
        }
