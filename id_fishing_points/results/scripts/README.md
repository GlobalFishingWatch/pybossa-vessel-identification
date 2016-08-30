Input:
    id_fishing_points_tasks.json
    id_fishing_points_task_runs.json
    gs://storage.googleapis.com/gfw-crowd/MMSI_YYYY_MM.json
    bq:pipeline_normalize.*

Output:
    id_fishing_points_classified_tracks.npz


The process is semi-automated:
First run

    python scripts/query_cogsog_tracks.py id_fishing_points

This will print a BQ query. Execute the query and store its result in
id_fishing_points_cogsog_tracks.csv, then run

    python scripts/convert_cogsog_tracks.py id_fishing_points
    python scripts/download_tracks.py id_fishing_points
    python scripts/join_results.py id_fishing_points

