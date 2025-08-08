import os, json, hashlib, pandas as pd, datetime as dt
import gspread
from google.oauth2.service_account import Credentials

REQUIRED_HEADERS = ['Type','Source','Title','Author/Company','Date','ExecutiveSummary','BusinessInsight','RelevanceScore','Link','CanonicalLink','PrimaryOrSecondary','DedupeKey','Status']

SHEET_ID_DEFAULT = "10JPJ33f64h6Wi8aTWi4XWaSFeFZYLn2Gyfx8_p6pzgg"
SHEET_TAB_DEFAULT = "sheet 1"

def _auth_client():
    keyfile = os.getenv("GCP_SERVICE_ACCOUNT_JSON_FILE")
    if keyfile and os.path.exists(keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            info = json.load(f)
    else:
        raise RuntimeError("Service account JSON file not found. Set GCP_SERVICE_ACCOUNT_JSON_FILE.")
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds)

def _ensure_headers(ws):
    first_row = ws.row_values(1)
    if first_row != REQUIRED_HEADERS:
        if first_row:
            ws.delete_row(1)
        ws.insert_row(REQUIRED_HEADERS, 1)

def open_sheet():
    sheet_id = os.getenv("SHEET_ID") or SHEET_ID_DEFAULT
    tab = os.getenv("SHEET_TAB") or SHEET_TAB_DEFAULT
    gc = _auth_client()
    sh = gc.open_by_key(sheet_id)
    try:
        ws = sh.worksheet(tab)
    except Exception:
        ws = sh.add_worksheet(title=tab, rows=1, cols=len(REQUIRED_HEADERS))
    _ensure_headers(ws)
    return ws

def compute_key(title: str, domain: str, date_str: str) -> str:
    base = (title or "").lower().strip() + "|" + (domain or "") + "|" + (date_str or "")
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def existing_keys(ws) -> set:
    values = ws.col_values(12)[1:]  # DedupeKey column
    return set([v for v in values if v])

def append_rows(ws, rows: list):
    if not rows:
        return
    ws.append_rows(rows, value_input_option="RAW")
