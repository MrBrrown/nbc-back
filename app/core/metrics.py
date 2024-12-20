from prometheus_client import Counter, Summary

uploaded_files_counter = Counter("uploaded_files", "Number of uploaded files")
downloaded_files_counter = Counter("downloaded_files", "Number of downloaded files")
deleted_files_counter = Counter("deleted_files", "Number of deleted files")
upload_time_summary = Summary("upload_time", "Time taken to upload files")