import os
import requests
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configuration
REPO = "oskuddar/trnL_DB"
GITHUB_TOKEN = os.getenv("GH_TOKEN")
DRIVE_FOLDER_ID = "1XpoWJhOBZdxMN5eNxbgIVszA5MDaFAil"

def get_github_traffic():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    # Fetch Views
    views_url = f"https://api.github.com/repos/{REPO}/traffic/views"
    views_data = requests.get(views_url, headers=headers).json()
    
    # Fetch Clones
    clones_url = f"https://api.github.com/repos/{REPO}/traffic/clones"
    clones_data = requests.get(clones_url, headers=headers).json()
    
    # Format into a simple row for today
    today = datetime.now().strftime("%Y-%m-%d")
    stats = {
        "date": today,
        "views_total": views_data.get("count", 0),
        "views_unique": views_data.get("uniques", 0),
        "clones_total": clones_data.get("count", 0),
        "clones_unique": clones_data.get("uniques", 0)
    }
    return stats

def upload_to_drive(stats):
    # Authenticate using the secret JSON stored in environment
    with open("credentials.json", "w") as f:
        f.write(os.getenv("GDRIVE_JSON"))
    
    creds = service_account.Credentials.from_service_account_file("credentials.json")
    service = build('drive', 'v3', credentials=creds)

    # Convert to CSV
    df = pd.DataFrame([stats])
    csv_file = "traffic_stats.csv"
    df.to_csv(csv_file, index=False)

    # Upload or Update logic (simplified: creates new file daily)
    file_metadata = {
        'name': f'traffic_{stats["date"]}.csv',
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(csv_file, mimetype='text/csv')
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

if __name__ == "__main__":
    data = get_github_traffic()
    upload_to_drive(data)