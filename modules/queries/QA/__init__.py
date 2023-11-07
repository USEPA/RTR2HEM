import os, shutil
import pandas as pd

from modules.html_writer import QAToHTML
from modules.utils import config

from modules.queries.QA.qa_base import QABase
from modules.queries.QA._01_SourceCatRecs import SourceCatRecs
from modules.queries.QA._02_UniqueFacilities import UniqueFacilities
from modules.queries.QA._03_UniqueSources import UniqueSources
from modules.queries.QA._04_Hemispheres import Hemispheres
from modules.queries.QA._05_ReleasePointFormat import ReleasePointFormat
from modules.queries.QA._06_ReleasePointType import ReleasePointType
from modules.queries.QA._07_PointParams import PointParams
from modules.queries.QA._08_LengthWidthFix import LengthWidthFix
from modules.queries.QA._09_AreaParamsVal import AreaParamsVal
from modules.queries.QA._10_VolParams import VolParams
from modules.queries.QA._11_LineParams import LineParams
from modules.queries.QA._12_HEM3Chem import HEM3Chem


def run_qa():
    results = {
        "_": QABase(),
        "queries": [
            SourceCatRecs(),
            UniqueFacilities(),
            UniqueSources(),
            Hemispheres(),
            ReleasePointFormat(),
            ReleasePointType(),
            PointParams(),
            LengthWidthFix(),
            AreaParamsVal(),
            VolParams(),
            LineParams(),
            HEM3Chem(),
        ],
    }

    QAToHTML(results)

    out_dst = copy_template(results["_"])
    writer = pd.ExcelWriter(
        out_dst, engine="openpyxl", mode="a", if_sheet_exists="overlay"
    )
    for result in results["queries"]:
        write_excel_sheet(writer, result.qa_df, result)
    writer.close()
    return result


def copy_template(base):
    template_src = os.path.join(config.out.templates_fp, f"{base.template_name}.xlsx")
    out_dst = os.path.join(config.out.output_dir, f"{base.filename}.xlsx")
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
