from typing import Any, Dict, List
import io
import pandas as pd
from app.core import utils_io as U
from app.services.note_data import get_note_data

EXPECTED_PREFIXES = (
    "[API]endpoint",
    "[API]Method",
    "[Request][Header]",
    "[Request][Params]",
    "[Request][Query]",
    "[Request][Body]",
)

def build_combination_excel(content: bytes, filename: str) -> bytes:
    df = U.read_table(content, filename)
    headers = [str(h).strip() for h in list(df.columns)]
    rows = df.values.tolist()

    # collect values per column (ignore empty)
    per_col = [[] for _ in headers]
    for r in rows:
        for i, _h in enumerate(headers):
            v = U.normalize_cell(r[i] if i < len(r) else None)
            if v is not None:
                per_col[i].append(v)
    # empty column -> [None]
    for i in range(len(per_col)):
        if not per_col[i]:
            per_col[i] = [None]

    combos = U.cartesian_product(per_col)
    out_rows: List[List[Any]] = []
    for combo in combos:
        out_row = []
        for i, h in enumerate(headers):
            val = combo[i]
            out_row.append("" if val is None else val)
        out_rows.append(out_row)

    out_df = pd.DataFrame(out_rows, columns=headers)
    
    # Use centralized note data
    note_df = pd.DataFrame(get_note_data())

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        out_df.to_excel(writer, index=False, sheet_name="combination")
        note_df.to_excel(writer, index=False, sheet_name="note")
    buf.seek(0)
    return buf.getvalue()
