import os
from src.utils import config

"""
Write QA results to HTML
"""


class QAToHTML:
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
            text-align: left;
            border: none;
            padding: 5px;
        }

        .QAtable th {
            font-size: 14pt;
            color: #4f81bd;
            border-bottom: 2px solid #4f81bd;
        }

        .QAtable td {
            font-size: 12pt;
            vertical-align: top;
            padding-bottom: 2rem;
        }
        
        .QAtable tr:nth-child(even) {
            background: #E0E0E0;
        }
    """

    def __init__(self, queries):
        self.data = [q.get() for q in queries["queries"]]
        self.filename = queries["_"].filename

        self.rcolor_map = {
            new_key: index_key
            for index_key, index_value in queries["_"].color_map.items()
            for new_key in index_value
        }

        table = self.build_table()
        self.write_html(table)

    def qa_results_to_html(self):
        table_body_str = ""
        for row in self.data:
            color = self.rcolor_map.get(row["QA_Outcome"], "#807b90")
            table_body_str += f"""
                <tr>
                    <td>{row['QA_Number']}</td>
                    <td>{row['QA_Title']}</td>
                    <td>
                        <strong style="color:{color};">{row['QA_Outcome']}</strong>
                        </br>{row['QA_Message']}
                    </td>
                </tr>
            """
        return table_body_str

    def build_table(self):
        table_header_str = f"""
            <tr>
                <th style="width: 2rem;">No.</th>
                <th style="width: 18rem;">Subject</th>
                <th style="width: 35rem;">Outcome</th>
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
        header_str = f"""
            <h1>RTR-to-HEM Processing Tool -- QA of Import Data</h1>
            <h3>Modeling File Table: {config.input_table}</h3>
            <h3>Detailed Findings: {self.filename}.xlsx</h3>
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
        out_dst = os.path.join(config.out.output_dir, f"{self.filename}.html")
        with open(out_dst, "w") as fh:
            fh.write(html_string)
        os.startfile(out_dst)
