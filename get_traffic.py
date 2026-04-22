import os
import requests
import pandas as pd
import io
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Configuration
REPO = "oskuddar/trnL_DB"
GITHUB_TOKEN = os.getenv("GH_TOKEN")
FILE_ID = "1bKSLV1cipiZSc6OAqBLTlN3bo-kX8CN9sx3t1urawMI" 

def get_github_traffic():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Fetch Views
    views_res = requests.get(f"https://api.github.com/repos/{REPO}/traffic/views", headers=headers).json()
    # Fetch Clones
    clones_res = requests.get(f"https://api.github.com/repos/{REPO}/traffic/clones", headers=headers).json()
    
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_views": views_res.get("count", 0),
        "unique_views": views_res.get("uniques", 0),
        "total_clones": clones_res.get("count", 0),
        "unique_clones": clones_res.get("uniques", 0)
    }

def update_drive_file(current_stats):
    with open("credentials.json", "w") as f:
        f.write(os.getenv("GDRIVE_JSON"))
    
    creds = service_account.Credentials.from_service_account_file("credentials.json")
    service = build('drive', 'v3', credentials=creds)

    # 1. Download existing data
    request = service.files().export_media(fileId=FILE_ID, mimeType='text/csv')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    fh.seek(0)
    try:
        df = pd.read_csv(fh)
    except Exception:
        # Create empty dataframe if sheet is blank
        cols = ["date", "total_views", "unique_views", "total_clones", "unique_clones", "daily_new_views", "daily_new_clones"]
        df = pd.DataFrame(columns=cols)

    # 2. Calculate Daily Info
    if not df.empty:
        last_row = df.iloc[-1]
        # Calculate difference (Current Total minus Previous Total)
        # We use max(0, ...) to ensure we don't get negative numbers if GitHub resets its 14-day window
        daily_new_views = max(0, current_stats["total_views"] - last_row["total_views"])
        daily_new_clones = max(0, current_stats["total_clones"] - last_row["total_clones"])
    else:
        # First run: Daily info equals the current total
        daily_new_views = current_stats["total_views"]
        daily_new_clones = current_stats["total_clones"]

    # 3. Add daily info to the stats dictionary
    current_stats["daily_new_views"] = daily_new_views
    current_stats["daily_new_clones"] = daily_new_clones

    # 4. Append and Upload
    new_row = pd.DataFrame([current_stats])
    df = pd.concat([df, new_row], ignore_index=True)
    
    local_csv = "temp_traffic.csv"
    df.to_csv(local_csv, index=False)

    media = MediaFileUpload(local_csv, mimetype='text/csv')
    service.files().update(fileId=FILE_ID, media_body=media).execute()
    print(f"Update complete. New views today: {daily_new_views}")

if __name__ == "__main__":
    data = get_github_traffic()
    update_drive_file(data)