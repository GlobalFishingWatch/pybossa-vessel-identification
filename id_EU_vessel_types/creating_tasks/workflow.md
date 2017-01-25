
Here is how to upload projects to this PyBossa project

All these python scripts should be run from this directory

1) Determine the mmsi that we want to load into the project. The way this is done is described in 1_get_input_mmsi.md. The mmsi should be saved into a file `to_classify_{today_date}.csv` -- `today_date` is just a variable I use to keep track of when I'm adding tasks. 

2) run `2_make_bigquery_table.py` and to create a bigquery table and download it. The variable today_date has to be updated to be the same as the filename 

3) run `3_make_tracks_histogram.py` to create the tracks, upload them, and create the histogram and upload it, and to create the csv file with the tasks in it

4) if there is an error, and you just need to create the tasks file, run `4_create_input_file.py`

Once this has been done, there should be a file in the home directory of this project `tasks_{today_date}.csv`. 