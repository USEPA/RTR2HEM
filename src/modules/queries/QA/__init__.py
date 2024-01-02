import os, shutil
import logging
import pandas as pd

from src.html_writer import QAToHTML
from src.utils import config

from src.modules.queries.QA.qa_base import QABase
from src.modules.queries.QA._01_SourceCatRecs import SourceCatRecs
from src.modules.queries.QA._02_UniqueFacilities import UniqueFacilities
from src.modules.queries.QA._03_UniqueSources import UniqueSources
from src.modules.queries.QA._04_Hemispheres import Hemispheres
from src.modules.queries.QA._05_ReleasePointFormat import ReleasePointFormat
from src.modules.queries.QA._06_ReleasePointType import ReleasePointType
from src.modules.queries.QA._07_PointParams import PointParams
from src.modules.queries.QA._08_LengthWidthFix import LengthWidthFix
from src.modules.queries.QA._09_AreaParamsVal import AreaParamsVal
from src.modules.queries.QA._10_VolParams import VolParams
from src.modules.queries.QA._11_LineParams import LineParams
from src.modules.queries.QA._12_HEM3Chem import HEM3Chem
from src.modules.queries.QA._13_GenericHgCr import GenericHgCr
from src.modules.queries.QA._14_GenericDF import GenericDF
from src.modules.queries.QA._15_UnscreenedPOMs import UnscreenedPOMs
from src.modules.queries.QA._16_SrcTypes import SrcTypes
from src.modules.queries.QA._17_EmissTots import EmissTots
from src.modules.queries.QA._18_ZeroEmissFac import ZeroEmissFac
from src.modules.queries.QA._19_FacSrcCounts import FacSrcCounts
from src.modules.queries.QA._20_BadSTCOFIPS import BadSTCOFIPS
from src.modules.queries.QA._21_MetalSpecs import MetalSpecs


def run_qa():
    logging.info("Running QA")
    fatal_err_found = False

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
            GenericHgCr(),
            GenericDF(),
            UnscreenedPOMs(),
            SrcTypes(),
            EmissTots(),
            ZeroEmissFac(),
            FacSrcCounts(),
            BadSTCOFIPS(),
            MetalSpecs(),
        ],
    }

    QAToHTML(results)

    out_dst = copy_template(results["_"])
    writer = pd.ExcelWriter(
        out_dst, engine="openpyxl", mode="a", if_sheet_exists="overlay"
    )
    for result in results["queries"]:
        if result.qa_out == "Fatal Error":
            fatal_err_found = True
        write_excel_sheet(writer, result.qa_df, result)
    writer.close()
    return fatal_err_found


def copy_template(base: QABase):
    template_src = os.path.join(config.out.templates_fp, f"{base.template_name}.xlsx")
    out_dst = os.path.join(config.out.output_dir, f"{base.filename}.xlsx")
    shutil.copyfile(template_src, out_dst)
    return out_dst


def write_excel_sheet(writer, df: pd.DataFrame, data: QABase):
    df.to_excel(
        writer,
        sheet_name=data.sheet_name,
        header=False,
        index=False,
        startrow=data.rowstart,
        startcol=data.colstart,
    )
