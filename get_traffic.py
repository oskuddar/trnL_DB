import os
import io
import requests
import pandas as pd
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


def get_github_traffic_daily_row():
    github_headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    github_views_response = requests.get(
        f"https://api.github.com/repos/{REPO}/traffic/views",
        headers=github_headers,
        params={"per": "day"},
        timeout=30
    )
    github_views_response.raise_for_status()
    github_views_payload = github_views_response.json()

    github_clones_response = requests.get(
        f"https://api.github.com/repos/{REPO}/traffic/clones",
        headers=github_headers,
        params={"per": "day"},
        timeout=30
    )
    github_clones_response.raise_for_status()
    github_clones_payload = github_clones_response.json()

    daily_views_by_date = {
        traffic_view_entry["timestamp"][:10]: {
            "daily_total_views": traffic_view_entry.get("count", 0),
            "daily_unique_views": traffic_view_entry.get("uniques", 0)
        }
        for traffic_view_entry in github_views_payload.get("views", [])
    }

    daily_clones_by_date = {
        traffic_clone_entry["timestamp"][:10]: {
            "daily_total_clones": traffic_clone_entry.get("count", 0),
            "daily_unique_clones": traffic_clone_entry.get("uniques", 0)
        }
        for traffic_clone_entry in github_clones_payload.get("clones", [])
    }

    available_traffic_dates = sorted(set(daily_views_by_date) | set(daily_clones_by_date))

    if not available_traffic_dates:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    latest_traffic_date = available_traffic_dates[-1]

    latest_traffic_row = {
        "date": latest_traffic_date,
        "daily_total_views": daily_views_by_date.get(latest_traffic_date, {}).get("daily_total_views", 0),
        "daily_unique_views": daily_views_by_date.get(latest_traffic_date, {}).get("daily_unique_views", 0),
        "daily_total_clones": daily_clones_by_date.get(latest_traffic_date, {}).get("daily_total_clones", 0),
        "daily_unique_clones": daily_clones_by_date.get(latest_traffic_date, {}).get("daily_unique_clones", 0),
        "cumulative_total_views": 0,
        "cumulative_unique_views": 0,
        "cumulative_total_clones": 0,
        "cumulative_unique_clones": 0
    }

    return pd.DataFrame([latest_traffic_row])


def get_google_drive_service():
    with open("credentials.json", "w") as credential_output_handle:
        credential_output_handle.write(os.getenv("GDRIVE_JSON"))

    google_drive_credentials = service_account.Credentials.from_service_account_file("credentials.json")
    return build("drive", "v3", credentials=google_drive_credentials)


def download_existing_traffic_table(google_drive_service):
    export_request = google_drive_service.files().export_media(
        fileId=FILE_ID,
        mimeType="text/csv"
    )

    downloaded_csv_buffer = io.BytesIO()
    google_drive_downloader = MediaIoBaseDownload(downloaded_csv_buffer, export_request)

    download_finished = False
    while download_finished is False:
        download_status, download_finished = google_drive_downloader.next_chunk()

    downloaded_csv_buffer.seek(0)

    try:
        existing_traffic_table = pd.read_csv(downloaded_csv_buffer)
    except Exception:
        existing_traffic_table = pd.DataFrame(columns=OUTPUT_COLUMNS)

    return existing_traffic_table


def standardize_existing_traffic_table(existing_traffic_table):
    if existing_traffic_table.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    standardized_traffic_table = existing_traffic_table.copy()

    if "date" not in standardized_traffic_table.columns:
        standardized_traffic_table["date"] = pd.NaT

    if "daily_total_views" not in standardized_traffic_table.columns and "daily_new_views" in standardized_traffic_table.columns:
        standardized_traffic_table["daily_total_views"] = standardized_traffic_table["daily_new_views"]

    if "daily_total_clones" not in standardized_traffic_table.columns and "daily_new_clones" in standardized_traffic_table.columns:
        standardized_traffic_table["daily_total_clones"] = standardized_traffic_table["daily_new_clones"]

    for required_column_name in OUTPUT_COLUMNS:
        if required_column_name not in standardized_traffic_table.columns:
            standardized_traffic_table[required_column_name] = 0

    standardized_traffic_table = standardized_traffic_table[OUTPUT_COLUMNS]

    standardized_traffic_table["date"] = pd.to_datetime(
        standardized_traffic_table["date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    standardized_traffic_table = standardized_traffic_table.dropna(subset=["date"])

    numeric_traffic_columns = [column_name for column_name in OUTPUT_COLUMNS if column_name != "date"]

    standardized_traffic_table[numeric_traffic_columns] = standardized_traffic_table[numeric_traffic_columns].apply(
        pd.to_numeric,
        errors="coerce"
    ).fillna(0).astype(int)

    standardized_traffic_table = standardized_traffic_table.sort_values("date")
    standardized_traffic_table = standardized_traffic_table.drop_duplicates(subset=["date"], keep="last")

    return standardized_traffic_table


def update_cumulative_columns(traffic_history_table):
    sorted_traffic_history_table = traffic_history_table.sort_values("date").reset_index(drop=True).copy()

    daily_metric_columns = [
        "daily_total_views",
        "daily_unique_views",
        "daily_total_clones",
        "daily_unique_clones"
    ]

    sorted_traffic_history_table[daily_metric_columns] = sorted_traffic_history_table[daily_metric_columns].apply(
        pd.to_numeric,
        errors="coerce"
    ).fillna(0).astype(int)

    sorted_traffic_history_table["cumulative_total_views"] = sorted_traffic_history_table["daily_total_views"].cumsum()
    sorted_traffic_history_table["cumulative_unique_views"] = sorted_traffic_history_table["daily_unique_views"].cumsum()
    sorted_traffic_history_table["cumulative_total_clones"] = sorted_traffic_history_table["daily_total_clones"].cumsum()
    sorted_traffic_history_table["cumulative_unique_clones"] = sorted_traffic_history_table["daily_unique_clones"].cumsum()

    return sorted_traffic_history_table[OUTPUT_COLUMNS]


def update_drive_file():
    google_drive_service = get_google_drive_service()

    existing_traffic_table = download_existing_traffic_table(google_drive_service)
    standardized_traffic_table = standardize_existing_traffic_table(existing_traffic_table)
    github_latest_daily_traffic_table = get_github_traffic_daily_row()

    combined_traffic_table = pd.concat(
        [standardized_traffic_table, github_latest_daily_traffic_table],
        ignore_index=True
    )

    combined_traffic_table["date"] = pd.to_datetime(
        combined_traffic_table["date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    combined_traffic_table = combined_traffic_table.dropna(subset=["date"])
    combined_traffic_table = combined_traffic_table.sort_values("date")
    combined_traffic_table = combined_traffic_table.drop_duplicates(subset=["date"], keep="last")

    updated_traffic_table = update_cumulative_columns(combined_traffic_table)

    local_csv_path = "temp_traffic.csv"
    updated_traffic_table.to_csv(local_csv_path, index=False)

    upload_media = MediaFileUpload(local_csv_path, mimetype="text/csv")
    google_drive_service.files().update(fileId=FILE_ID, media_body=upload_media).execute()

    latest_traffic_row = updated_traffic_table.iloc[-1]

    print(
        "Update complete. "
        f"Latest date: {latest_traffic_row['date']}. "
        f"Daily views: {latest_traffic_row['daily_total_views']}. "
        f"Daily clones: {latest_traffic_row['daily_total_clones']}. "
        f"Cumulative views: {latest_traffic_row['cumulative_total_views']}. "
        f"Cumulative clones: {latest_traffic_row['cumulative_total_clones']}."
    )


if __name__ == "__main__":
    update_drive_file()
