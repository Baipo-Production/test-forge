from pathlib import Path
from typing import Tuple
import re
import pandas as pd
from app.core.config import STORAGE_PATH

def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-]+", "_", name).strip("_") or "TestForgeSuite"

def setup_workspace(test_name: str) -> Tuple[Path, Path, Path]:
    root = STORAGE_PATH / safe_name(test_name)
    gen = root / "generated"
    rep = root / "Report"
    gen.mkdir(parents=True, exist_ok=True)
    rep.mkdir(parents=True, exist_ok=True)
    return root, gen, rep

ROBOT_HEADER = """*** Settings ***
Library    RequestsLibrary
Library    JSONLibrary
Library    Collections
Suite Setup    Create Session    api    {base_url}

*** Test Cases ***
"""

# Assertion operators for dynamic validation
ASSERTION_OPERATORS = {
    "eq": "eq",           # Equal (default)
    "ne": "ne",           # Not equal
    "gt": "gt",           # Greater than
    "lt": "lt",           # Less than
    "contains": "contains",  # Substring present
    "regex": "regex",     # Regular expression match
    "between": "between", # Numeric range (low,high)
}

def parse_field_meta(raw: str):
    """
    Parse field with operator and type tag.
    Examples:
        "age:gt[Type:int]" -> ("age", "gt", "int")
        "score:between[Type:float]" -> ("score", "between", "float")
        "name[Type:string]" -> ("name", "eq", "string")
        "active[Type:bool]" -> ("active", "eq", "bool")
        "id" -> ("id", "eq", None)
    
    Args:
        raw: Raw field string with optional operator and type tag
    
    Returns:
        tuple: (field_name, operator, data_type)
    """
    # Extract type tag if present: [Type:int], [Type:float], etc.
    type_match = re.search(r'\[Type:([^]]+)\]\s*$', raw, flags=re.IGNORECASE)
    dtype = type_match.group(1).strip().lower() if type_match else None
    
    # Remove type tag from string
    core = re.sub(r'\[Type:[^]]+\]\s*$', '', raw, flags=re.IGNORECASE).strip()
    
    # Parse operator from remaining string
    if ":" in core:
        parts = core.rsplit(":", 1)
        field = parts[0].strip()
        op = parts[1].strip().lower()
        if op not in ASSERTION_OPERATORS:
            op = "eq"  # fallback to default
    else:
        field = core
        op = "eq"  # default operator
    
    return field, op, dtype

def cast_value(value_raw: str, dtype: str):
    """
    Cast string value to appropriate type.
    
    Args:
        value_raw: Raw string value
        dtype: Target data type (int, float, bool, string)
    
    Returns:
        Casted value or original string if conversion fails
    """
    if dtype is None or dtype == "string":
        return value_raw
    
    if dtype in ("int", "integer"):
        try:
            return int(value_raw)
        except (ValueError, TypeError):
            return value_raw
    
    if dtype in ("float", "double", "number"):
        try:
            return float(value_raw)
        except (ValueError, TypeError):
            return value_raw
    
    if dtype in ("bool", "boolean"):
        v = str(value_raw).strip().lower()
        return v in ("1", "true", "yes", "y", "t")
    
    return value_raw

def parse_assertion(field_key: str, expected_raw: str):
    """
    DEPRECATED: Use parse_field_meta instead.
    Kept for backward compatibility.
    """
    field, op, _ = parse_field_meta(field_key)
    return field, op, expected_raw

def generate_robot_cases_from_excel(excel_path: Path, gen_dir: Path):
    df = pd.read_excel(excel_path, sheet_name=0, dtype=str).fillna("")
    tests = []
    
    # Extract base URL from first row's endpoint
    base_url = "http://localhost"
    if len(df) > 0:
        first_endpoint = df.iloc[0].get("[API]endpoint", "")
        if first_endpoint.startswith("http"):
            # Parse base URL (e.g., http://mockoon.ariyanaragroup.com)
            parts = first_endpoint.split("/")
            if len(parts) >= 3:
                base_url = f"{parts[0]}//{parts[2]}"
    
    for i, row in df.iterrows():
        tc_name = f"TC_{i+1:03d}"
        endpoint = row.get("[API]endpoint", "")
        method = (row.get("[API]Method", "POST") or "POST").upper()
        resp_code = row.get("[Response][API]status", "")
        
        # Convert full URL to relative path if needed
        if endpoint.startswith("http"):
            endpoint = "/" + "/".join(endpoint.split("/")[3:])
        
        # Extract expected response data
        expected_body = {}
        expected_header = {}
        
        for k, v in row.items():
            if not v:
                continue
            if k.startswith("[Response][Body]"):
                raw = k.replace("[Response][Body]", "", 1)
                field_name, op, dtype = parse_field_meta(raw)
                # Store as tuple: (value, data_type)
                key = field_name + (":" + op if op != "eq" else "")
                expected_body[key] = (v, dtype)
            elif k.startswith("[Response][Header]"):
                raw = k.replace("[Response][Header]", "", 1)
                field_name, op, dtype = parse_field_meta(raw)
                key = field_name + (":" + op if op != "eq" else "")
                expected_header[key] = (v, dtype)
        
        # Extract request data
        body = {k.replace("[Request][Body]", ""): v for k, v in row.items() if k.startswith("[Request][Body]") and v}
        headers = {k.replace("[Request][Header]", ""): v for k, v in row.items() if k.startswith("[Request][Header]") and v}
        params = {k.replace("[Request][Params]", ""): v for k, v in row.items() if k.startswith("[Request][Params]") and v}
        query = {k.replace("[Request][Query]", ""): v for k, v in row.items() if k.startswith("[Request][Query]") and v}

        lines = [ROBOT_HEADER.format(base_url=base_url)]
        lines.append(f"{tc_name}")
        
        # Log API request details
        lines.append(f"    Log    ========== REQUEST ==========    console=yes")
        lines.append(f"    Log    Method: {method}    console=yes")
        lines.append(f"    Log    Endpoint: {endpoint}    console=yes")
        
        # Build request parameters - use Create Dictionary only if there's data
        if headers:
            dict_str = "    ".join([f"{k}={v}" for k, v in headers.items()])
            lines.append(f"    ${'{'}headers{'}'}=    Create Dictionary    {dict_str}")
            lines.append(f"    Log    Headers: ${'{'}headers{'}'}    console=yes")
        if params:
            dict_str = "    ".join([f"{k}={v}" for k, v in params.items()])
            lines.append(f"    ${'{'}params{'}'}=    Create Dictionary    {dict_str}")
            lines.append(f"    Log    Params: ${'{'}params{'}'}    console=yes")
        if query:
            dict_str = "    ".join([f"{k}={v}" for k, v in query.items()])
            lines.append(f"    ${'{'}query{'}'}=    Create Dictionary    {dict_str}")
            lines.append(f"    Log    Query: ${'{'}query{'}'}    console=yes")
        if body:
            dict_str = "    ".join([f"{k}={v}" for k, v in body.items()])
            lines.append(f"    ${'{'}payload{'}'}=    Create Dictionary    {dict_str}")
            lines.append(f"    Log    Body: ${'{'}payload{'}'}    console=yes")
        
        # Build API call with only the parameters that exist
        call_parts = [f"${'{'}resp{'}'}=", f"{method} On Session", "api", endpoint]
        if query:
            call_parts.append(f"params=${'{'}query{'}'}")
        if headers:
            call_parts.append(f"headers=${'{'}headers{'}'}")
        if body:
            call_parts.append(f"json=${'{'}payload{'}'}")
        
        # Always add expected_status=any to prevent RequestsLibrary from raising HTTPError
        # This allows the test to validate the actual status code instead
        call_parts.append("expected_status=any")
        
        lines.append("    " + "    ".join(call_parts))
        
        # Log API response details
        lines.append(f"    Log    ========== RESPONSE ==========    console=yes")
        lines.append(f"    Log    Status Code: ${'{'}resp.status_code{'}'}    console=yes")
        lines.append(f"    Log    Response Headers: ${'{'}resp.headers{'}'}    console=yes")
        lines.append(f"    Log    Response Body: ${'{'}resp.text{'}'}    console=yes")
        
        # Validate status code
        if str(resp_code).strip():
            lines.append(f"    Should Be Equal As Integers    ${'{'}resp.status_code{'}'}    {resp_code}")
        
        # Validate response headers
        if expected_header:
            for raw_key, (header_value_raw, dtype) in expected_header.items():
                field_name, op, _ = parse_field_meta(raw_key)
                header_value = cast_value(header_value_raw, dtype)
                
                # Headers support: eq, ne, contains, regex
                if op == "ne":
                    lines.append(f"    Should Not Be Equal    ${'{'}resp.headers['{field_name}']{'}'}    {header_value}")
                elif op == "contains":
                    lines.append(f"    Should Contain    ${'{'}resp.headers['{field_name}']{'}'}    {header_value}")
                elif op == "regex":
                    lines.append(f"    Should Match Regexp    ${'{'}resp.headers['{field_name}']{'}'}    {header_value}")
                else:  # eq (default)
                    lines.append(f"    Should Be Equal    ${'{'}resp.headers['{field_name}']{'}'}    {header_value}")
        
        # Validate response body
        if expected_body:
            lines.append(f"    ${'{'}json{'}'}=    Set Variable    ${'{'}resp.json(){'}'}")
            for raw_key, (expected_value_raw, dtype) in expected_body.items():
                field_name, op, _ = parse_field_meta(raw_key)
                expected_value = cast_value(expected_value_raw, dtype)
                
                # Get value from JSON
                lines.append(f"    ${'{'}value{'}'}=    Get Value From Json    ${'{'}json{'}'}    $.{field_name}")
                
                # Convert to number for numeric comparisons
                if op in ("gt", "lt", "between"):
                    lines.append(f"    ${'{'}num{'}'}=    Convert To Number    ${'{'}value[0]{'}'}")
                
                # Apply assertion based on operator
                if op == "eq":
                    if dtype in ("int", "integer"):
                        lines.append(f"    Should Be Equal As Integers    ${'{'}value[0]{'}'}    {expected_value}")
                    elif dtype in ("float", "double", "number"):
                        lines.append(f"    Should Be Equal As Numbers    ${'{'}value[0]{'}'}    {expected_value}")
                    elif dtype in ("bool", "boolean"):
                        bool_str = "True" if expected_value else "False"
                        lines.append(f"    Should Be Equal    ${'{'}value[0]{'}'}    {bool_str}")
                    else:
                        lines.append(f"    Should Be Equal    ${'{'}value[0]{'}'}    {expected_value}")
                elif op == "ne":
                    lines.append(f"    Should Not Be Equal    ${'{'}value[0]{'}'}    {expected_value}")
                elif op == "gt":
                    lines.append(f"    Should Be True    ${'{'}num{'}'} > {expected_value}")
                elif op == "lt":
                    lines.append(f"    Should Be True    ${'{'}num{'}'} < {expected_value}")
                elif op == "contains":
                    lines.append(f"    Should Contain    ${'{'}value[0]{'}'}    {expected_value}")
                elif op == "regex":
                    lines.append(f"    Should Match Regexp    ${'{'}value[0]{'}'}    {expected_value}")
                elif op == "between":
                    # Expected format: "low,high" or "low:high" or "low;high"
                    bounds = [b.strip() for b in re.split(r'[,;:]', str(expected_value_raw)) if b.strip()]
                    low = cast_value(bounds[0], dtype) if len(bounds) > 0 else 0
                    high = cast_value(bounds[1], dtype) if len(bounds) > 1 else low
                    lines.append(f"    Should Be True    ${'{'}num{'}'} >= {low} and ${'{'}num{'}'} <= {high}")
                else:
                    # Fallback to equality
                    lines.append(f"    Should Be Equal    ${'{'}value[0]{'}'}    {expected_value}")

        content = "\n".join(lines) + "\n"
        (gen_dir / f"{tc_name}.robot").write_text(content, encoding="utf-8")
        tests.append(tc_name)
    return tests
