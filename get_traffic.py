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

    # Fetch daily views
    views_res = requests.get(
        f"https://api.github.com/repos/{REPO}/traffic/views",
        headers=headers,
        params={"per": "day"}
    ).json()

    # Fetch daily clones
    clones_res = requests.get(
        f"https://api.github.com/repos/{REPO}/traffic/clones",
        headers=headers,
        params={"per": "day"}
    ).json()

    views_by_date = {
        view_entry["timestamp"][:10]: {
            "daily_total_views": view_entry.get("count", 0),
            "daily_unique_views": view_entry.get("uniques", 0)
        }
        for view_entry in views_res.get("views", [])
    }

    clones_by_date = {
        clone_entry["timestamp"][:10]: {
            "daily_total_clones": clone_entry.get("count", 0),
            "daily_unique_clones": clone_entry.get("uniques", 0)
        }
        for clone_entry in clones_res.get("clones", [])
    }

    available_dates = sorted(set(views_by_date) | set(clones_by_date))

    if available_dates:
        report_date = available_dates[-1]
    else:
        report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return {
        "date": report_date,
        "daily_total_views": views_by_date.get(report_date, {}).get("daily_total_views", 0),
        "daily_unique_views": views_by_date.get(report_date, {}).get("daily_unique_views", 0),
        "daily_total_clones": clones_by_date.get(report_date, {}).get("daily_total_clones", 0),
        "daily_unique_clones": clones_by_date.get(report_date, {}).get("daily_unique_clones", 0)
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

    # 2. Convert old column names if the previous CSV used the original format
    old_column_map = {
        "daily_new_views": "daily_total_views",
        "daily_new_clones": "daily_total_clones"
    }

    df = df.rename(columns=old_column_map)

    for column_name in OUTPUT_COLUMNS:
        if column_name not in df.columns:
            df[column_name] = 0

    df = df[OUTPUT_COLUMNS]

    # 3. Clean dates and numeric columns
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date"])

    numeric_columns = [column_name for column_name in OUTPUT_COLUMNS if column_name != "date"]

    df[numeric_columns] = df[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce"
    ).fillna(0).astype(int)

    # 4. Add only one row for the latest daily GitHub report
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

    # 5. Prevent duplicate dates if the workflow is run more than once on the same day
    df = df.sort_values("date")
    df = df.drop_duplicates(subset=["date"], keep="last")

    # 6. Calculate cumulative totals from saved daily rows
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

    latest_row = df.iloc[-1]

    print(
        f"Update complete. Date: {latest_row['date']}. "
        f"Daily views: {latest_row['daily_total_views']}. "
        f"Daily clones: {latest_row['daily_total_clones']}. "
        f"Cumulative views: {latest_row['cumulative_total_views']}. "
        f"Cumulative clones: {latest_row['cumulative_total_clones']}."
    )


if __name__ == "__main__":
    data = get_github_traffic()
    update_drive_file(data)
