import os
import requests
import pandas as pd
import io
from datetime import datetime, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Configuration
REPO = "oskuddar/trnL_DB"
GITHUB_TOKEN = os.getenv("GH_TOKEN")
FILE_ID = "1bKSLV1cipiZSc6OAqBLTlN3bo-kX8CN9sx3t1urawMI"

OUTPUT_COLUMNS = [
    "date",
    "daily_total_views",
    "daily_unique_views",
    "daily_total_clones",
    "daily_unique_clones",
    "cumulative_total_views",
    "cumulative_unique_views",
    "cumulative_total_clones",
    "cumulative_unique_clones"
]

def get_github_traffic():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Fetch Views
    views_res = requests.get(
        f"https://api.github.com/repos/{REPO}/traffic/views",
        headers=headers,
        params={"per": "day"}
    ).json()

    # Fetch Clones
    clones_res = requests.get(
        f"https://api.github.com/repos/{REPO}/traffic/clones",
        headers=headers,
        params={"per": "day"}
    ).json()

    today_views = {"count": 0, "uniques": 0}
    today_clones = {"count": 0, "uniques": 0}

    for view_entry in views_res.get("views", []):
        if view_entry.get("timestamp", "")[:10] == today_date:
            today_views = view_entry
            break

    for clone_entry in clones_res.get("clones", []):
        if clone_entry.get("timestamp", "")[:10] == today_date:
            today_clones = clone_entry
            break

    return {
        "date": today_date,
        "daily_total_views": today_views.get("count", 0),
        "daily_unique_views": today_views.get("uniques", 0),
        "daily_total_clones": today_clones.get("count", 0),
        "daily_unique_clones": today_clones.get("uniques", 0)
    }

def update_drive_file(current_stats):
    with open("credentials.json", "w") as f:
        f.write(os.getenv("GDRIVE_JSON"))

    creds = service_account.Credentials.from_service_account_file("credentials.json")
    service = build("drive", "v3", credentials=creds)

    # 1. Download existing data
    request = service.files().export_media(fileId=FILE_ID, mimeType="text/csv")
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False

    while done is False:
        status, done = downloader.next_chunk()

    fh.seek(0)

    try:
        df = pd.read_csv(fh)
    except Exception:
        df = pd.DataFrame(columns=OUTPUT_COLUMNS)

    if df.empty:
        df = pd.DataFrame(columns=OUTPUT_COLUMNS)

    # 2. Keep the required columns
    for column_name in OUTPUT_COLUMNS:
        if column_name not in df.columns:
            df[column_name] = 0

    df = df[OUTPUT_COLUMNS]

    # 3. Clean existing data
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date"])

    numeric_columns = [column_name for column_name in OUTPUT_COLUMNS if column_name != "date"]

    df[numeric_columns] = df[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce"
    ).fillna(0).astype(int)

    # 4. Add today's row only
    new_row = pd.DataFrame([current_stats])

    for column_name in OUTPUT_COLUMNS:
        if column_name not in new_row.columns:
            new_row[column_name] = 0

    new_row = new_row[OUTPUT_COLUMNS]
    new_row["date"] = pd.to_datetime(new_row["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    new_row[numeric_columns] = new_row[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce"
    ).fillna(0).astype(int)

    df = pd.concat([df, new_row], ignore_index=True)

    # 5. Prevent duplicate row if workflow runs more than once today
    df = df.sort_values("date")
    df = df.drop_duplicates(subset=["date"], keep="last")

    # 6. Recalculate cumulative columns from saved daily rows
    df["cumulative_total_views"] = df["daily_total_views"].cumsum()
    df["cumulative_unique_views"] = df["daily_unique_views"].cumsum()
    df["cumulative_total_clones"] = df["daily_total_clones"].cumsum()
    df["cumulative_unique_clones"] = df["daily_unique_clones"].cumsum()

    df = df[OUTPUT_COLUMNS]

    # 7. Upload updated CSV
    local_csv = "temp_traffic.csv"
    df.to_csv(local_csv, index=False)

    media = MediaFileUpload(local_csv, mimetype="text/csv")
    service.files().update(fileId=FILE_ID, media_body=media).execute()

    print(
        f"Update complete. Date: {current_stats['date']}. "
        f"Daily views: {current_stats['daily_total_views']}. "
        f"Daily clones: {current_stats['daily_total_clones']}."
    )

if __name__ == "__main__":
    data = get_github_traffic()
    update_drive_file(data)
