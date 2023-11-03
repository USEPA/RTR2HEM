import os, shutil
import pandas as pd

from modules.utils import config
from modules.html_writer import QAToHTML

from modules.queries.QA.qa_base import QABase
from modules.queries.QA._01_SourceCatRecs import SourceCatRecs
from modules.queries.QA._02_UniqueFacilities import UniqueFacilities
from modules.queries.QA._03_UniqueSources import UniqueSources
from modules.queries.QA._04_Hemispheres import Hemispheres


def run_qa():
    results = {
        "_": QABase(),
        "queries": [
            SourceCatRecs(),
            UniqueFacilities(),
            UniqueSources(),
            Hemispheres(),
        ],
    }

    QAToHTML(results)

    filename = results["_"].filename
    out_dst = copy_template(filename, results["_"])
    writer = pd.ExcelWriter(
        out_dst, engine="openpyxl", mode="a", if_sheet_exists="overlay"
    )
    for result in results["queries"]:
        write_excel_sheet(writer, result.qa_df, result)
    writer.close()

    return result


def copy_template(name, result):
    template_src = os.path.join(config.out.templates_fp, f"{result.template_name}.xlsx")
    out_dst = os.path.join(config.out.output_dir, f"{name}.xlsx")
    shutil.copyfile(template_src, out_dst)
    return out_dst


def write_excel_sheet(writer, df, data):
    df.to_excel(
        writer,
        sheet_name=data.sheet_name,
        header=False,
        index=False,
        startrow=data.rowstart,
        startcol=data.colstart,
    )
