# heuristics.py
import re
import math
import pandas as pd

def compute_answer_from_context(full_text, tables):
    if full_text is None:
        full_text = ""

    t = full_text
    tl = t.lower()

    # SUM OF NAMED COLUMN
    m = re.search(r'sum of (?:the )?"?([a-z0-9_ ]{2,60})"? column', tl)
    if m:
        col = m.group(1).strip()
        for df in tables:
            cols = [str(c).lower() for c in df.columns]
            if col in cols:
                colname = df.columns[cols.index(col)]
                numeric = pd.to_numeric(df[colname], errors="coerce").dropna()
                if not numeric.empty:
                    s = numeric.sum()
                    return int(s) if float(s).is_integer() else float(s)

    # VALUE COL ON PAGE N
    m2 = re.search(r'value"? column in the table on page (\d+)', tl)
    if m2:
        page = int(m2.group(1))
        if 1 <= page <= len(tables):
            df = tables[page - 1]
            cols = [c.lower() for c in df.columns]
            if "value" in cols:
                cname = df.columns[cols.index("value")]
                numeric = pd.to_numeric(df[cname], errors="coerce").dropna()
                if not numeric.empty:
                    s = numeric.sum()
                    return int(s) if float(s).is_integer() else float(s)

    # HOW MANY <TERM>
    m3 = re.search(r'how many ([a-z0-9_ ]{2,40})', tl)
    if m3:
        term = m3.group(1).strip()
        for df in tables:
            cols = [c.lower() for c in df.columns]
            if term in cols:
                return df[df.columns[cols.index(term)]].dropna().shape[0]

    # DIRECT ANSWER:
    m4 = re.search(r'answer[:\s]+(-?\d+(?:\.\d+)?)', t, flags=re.I)
    if m4:
        v = float(m4.group(1))
        return int(v) if v.is_integer() else float(v)

    # FALLBACK: LARGEST NUMERIC SUM
    best = None
    for df in tables:
        for col in df.columns:
            try:
                numeric = pd.to_numeric(df[col], errors="coerce")
                numeric = numeric[numeric.notna()]
                if len(numeric) > 0:
                    s = numeric.sum()
                    if best is None or abs(s) > abs(best):
                        best = s
            except:
                continue
    if best is not None:
        return int(best) if float(best).is_integer() else float(best)

    return None
