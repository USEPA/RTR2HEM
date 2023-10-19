import pandas as pd
from modules.queries.QA import run_qa


"""
will need to add a button as an additional step in GUI
"""


class QA:
    def __init__(self):
        pass

    def run(self):
        results = run_qa()
        df = pd.DataFrame(results)

        print("!")
