import pandas as pd

"""
Write QA results to HTML
"""


class HTMLWriter:
    css = """
        body {
            font-family: Calibri;
            margin-left: 1rem;
        }

        h1,h2,h3,h4,h5,h6 {
            color: #4f81bd;
            margin-top: 5px;
            margin-bottom: 5px;
        }

        h3,h4,h5,h6 {
            margin-left: 1rem;
        }

        .QAtable {
            table-layout: fixed;
            border-collapse: collapse;
            margin-left: 1rem;            
        }

        .QAtable td,th {
            padding: 5px;
        }

        .QAtable th {
            font-size: 14pt;
            text-align: left;
            color: #4f81bd;
            border: none;
            border-bottom: 2px solid #4f81bd;
        }

        .QAtable td {
            font-size: 12pt;
            text-align: left;
            border: none;
            padding-bottom: 2rem;
        }
        
        .QAtable tr:nth-child(even) {
            background: #E0E0E0;
        }

        .QAtable tr:hover {
            background: silver;
            cursor: pointer;
        }
    """

    def __init__(self):
        from modules.queries.QA.qa_base import QABase

        # note -- outcome, message, result all go into the same cell
        self.data = [
            {
                "params": {},
                "query": {
                    "QA_Number": "01",
                    "QA_Title": "my title",
                    "QA_Outcome": "my outcome",
                    "QA_Message": "my msg",
                    "QA_Result": "my result",
                },
            },
            {
                "params": {},
                "query": {
                    "QA_Number": "02",
                    "QA_Title": "Pollutants that Cannot be Modeled for Inhalation Risk/Hazard",
                    "QA_Outcome": "As expected, all records have positive latitude values (Y coordinates) and negative longitude values (X coordinates).",
                    "QA_Message": "my second message",
                    "QA_Result": "my second result",
                },
            },
        ]
        table = self.build_table()
        self.write_html(table)
        print("!")

    def qa_results_to_html(self):
        table_body_str = ""
        for row in self.data:
            row = row["query"]
            table_body_str += f"""
                <tr>
                    <td>{row['QA_Number']}</td>
                    <td>{row['QA_Title']}</td>
                    <td>{row['QA_Outcome']}</td>
                </tr>
            """
        return table_body_str

    def build_table(self):
        table_header_str = f"""
            <tr>
                <th style="width: 2rem;">No.</th>
                <th style="width: 18rem;">Subject</th>
                <th style="width: 35rem">Outcome</th>
            </tr>
        """
        table_body_str = self.qa_results_to_html()
        table = f"""
            <table class="QAtable">
                <thead>{table_header_str}</thead>
                <tbody>{table_body_str}</tbody>
            </table>
        """
        return table

    def write_html(self, table):
        # TODO update
        header_str = f"""
            <h1>RTR-to-HEM Processing Tool -- QA of Import Data</h1>
            <h3>Modeling File Table: Refractories_WholeFacil_ATAGFormat_20200918</h3>
            <h3>Detailed Findings: Refractories20200918_RTRtoHEMandTier1_QA_20200921.xlsx</h3>
        """

        html_string = f"""
            <html>
            <style>{self.css}</style>
            <body>
                {header_str}
                {table}
            </body>
            </html>
        """
        with open("test.html", "w") as fh:
            fh.write(html_string)
