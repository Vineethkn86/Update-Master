from kite_login import kite_login
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("Tradelog.json", scopes=scope)
client = gspread.authorize(creds)

SHEET_NAME = "Historical data"                # Your Google Sheet name
sheet_master = client.open(SHEET_NAME).worksheet("Master_Options")

kite = kite_login()
inst_df = pd.DataFrame(kite.instruments("NFO"))
inst_df['expiry'] = pd.to_datetime(inst_df['expiry'], errors='coerce')

# ---------- Filter NIFTY CE/PE options ----------
nifty_opts = inst_df[
    (inst_df['name'] == 'NIFTY') &
    (inst_df['instrument_type'].isin(['CE', 'PE'])) &
    (inst_df['expiry'].notna()) 
]

# Keep relevant columns
nifty_opts = nifty_opts[['tradingsymbol', 'expiry', 'strike', 'instrument_type']].sort_values(
    ['expiry', 'strike', 'instrument_type']
)

nifty_opts['expiry'] = nifty_opts['expiry'].dt.strftime("%Y-%m-%d")

sheet_master.clear()
sheet_master.update(
    [nifty_opts.columns.values.tolist()] + nifty_opts.values.tolist()
)

print(f"✅ Written {len(nifty_opts)} rows of NIFTY options to Google Sheet.")
