First run:

```python download_results.py PROJECT_NAME```

This downloads `id_fishing_points_tasks.json` and
`id_fishing_points_task_runs.json`.

Then run:

```python scripts/extract_ranges --download PROJECT_NAME```

This downloads the project results, converts them to time
ranges and stores the results in `PROJECT_NAME_ranges.csv`.

If desired, `mussidae/scripts/download_ais_for_ranges.py` can
be used to download the corresponding AIS data and tag it with
fishing scores based on the PyBossa data.
