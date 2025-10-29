from typing import Any, Dict, List, Tuple
import io, re, json
import pandas as pd

def read_table(content: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith(".csv"):
        return pd.read_csv(io.BytesIO(content), dtype=str).fillna("")
    return pd.read_excel(io.BytesIO(content), dtype=str).fillna("")

def normalize_cell(v: Any):
    if v is None: return None
    s = str(v).strip()
    if s == "": return None
    if s.lower() == "true": return True
    if s.lower() == "false": return False
    try:
        if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
            return int(s)
        f = float(s); return f
    except: return s

def tokenize_body_path(path: str):
    parts = []
    for m in re.finditer(r"([^[.\]]+)|\[(\d+)\]", path):
        if m.group(1): parts.append(m.group(1))
        else: parts.append(int(m.group(2)))
    return parts

def assign_by_path(target: dict, path: str, value: Any):
    import re
    def tokens(p: str):
        out = []
        for m in re.finditer(r"([^[.\]]+)|\[(\d+)\]", p):
            if m.group(1): out.append(m.group(1))
            else: out.append(int(m.group(2)))
        return out
    obj = target
    ts = tokens(path)
    for i, t in enumerate(ts):
        last = i == len(ts) - 1
        if isinstance(t, str):
            if last: obj[t] = value
            else:
                nxt = ts[i+1]
                if t not in obj or obj[t] is None:
                    obj[t] = [] if isinstance(nxt, int) else {}
                obj = obj[t]
        else:
            if not isinstance(obj, list):
                obj_idx = []
                obj = []
            while len(obj) <= t: obj.append({})
            if last: obj[t] = value
            else:
                nxt = ts[i+1]
                if obj[t] is None: obj[t] = [] if isinstance(nxt, int) else {}
                obj = obj[t]

def apply_params(path: str, params: Dict[str, Any]) -> str:
    return re.sub(r"\{([^}]+)\}", lambda m: str(params.get(m.group(1), f"{{{m.group(1)}}}")), path)

def cartesian_product(arrays: List[List[Any]]):
    out = [[]]
    for arr in arrays:
        out = [prev + [v] for prev in out for v in arr]
    return out
