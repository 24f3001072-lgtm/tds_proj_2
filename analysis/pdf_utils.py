# pdf_utils.py
import pdfplumber
import pandas as pd
from io import BytesIO

def parse_pdf_bytes(b: bytes):
    text = ""
    tables = []
    try:
        with pdfplumber.open(BytesIO(b)) as pdf:
            for p in pdf.pages:
                txt = p.extract_text() or ""
                text += "\n" + txt
                tbls = p.extract_tables() or []
                for t in tbls:
                    if len(t) >= 2:
                        df = pd.DataFrame(t[1:], columns=t[0])
                    else:
                        df = pd.DataFrame(t)
                    tables.append(df)
    except:
        pass
    return text, tables
