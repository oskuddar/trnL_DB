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
# Your specific Google Sheet ID
FILE_ID = "1bKSLV1cipiZSc6OAqBLTlN3bo-kX8CN9sx3t1urawMI" 

def get_github_traffic():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Fetch Views
    views_url = f"https://api.github.com/repos/{REPO}/traffic/views"
    views_res = requests.get(views_url, headers=headers)
    views_data = views_res.json()
    
    # Fetch Clones
    clones_url = f"https://api.github.com/repos/{REPO}/traffic/clones"
    clones_res = requests.get(clones_url, headers=headers)
    clones_data = clones_res.json()
    
    today = datetime.now().strftime("%Y-%m-%d")
    stats = {
        "date": today,
        "views_total": views_data.get("count", 0),
        "views_unique": views_data.get("uniques", 0),
        "clones_total": clones_data.get("count", 0),
        "clones_unique": clones_data.get("uniques", 0)
    }
    return stats

def update_drive_file(new_stats):
    # 1. Setup Credentials
    with open("credentials.json", "w") as f:
        f.write(os.getenv("GDRIVE_JSON"))
    
    creds = service_account.Credentials.from_service_account_file("credentials.json")
    service = build('drive', 'v3', credentials=creds)

    # 2. Download the Google Sheet as a CSV
    # This bypasses quota because the file already exists in your storage
    request = service.files().export_media(fileId=FILE_ID, mimeType='text/csv')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    # 3. Append today's data to the data we just downloaded
    fh.seek(0)
    try:
        df = pd.read_csv(fh)
    except pd.errors.EmptyDataError:
        # If the sheet is brand new and empty, create the headers
        df = pd.DataFrame(columns=["date", "views_total", "views_unique", "clones_total", "clones_unique"])

    new_row = pd.DataFrame([new_stats])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Save the updated table locally for a moment
    local_csv = "temp_traffic.csv"
    df.to_csv(local_csv, index=False)

    # 4. Upload the updated data back to Google Drive
    media = MediaFileUpload(local_csv, mimetype='text/csv')
    service.files().update(fileId=FILE_ID, media_body=media).execute()
    print(f"Successfully updated Google Sheet for {new_stats['date']}")

if __name__ == "__main__":
    data = get_github_traffic()
    update_drive_file(data)