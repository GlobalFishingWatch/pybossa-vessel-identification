from __future__ import print_function
import os
import json
import subprocess


def download_tracks(dataset_name):
    """Download PyBossa tracks from GCS

    Args
    ====
    dataset_name : str
        name of the dataset to download tracks from.

    Tracks are assumed to reside in `gs://gfw-crowd/`.

    The project task list is assumed to exist at `./{datset_name}_tasks.json`

    Files are downloaded to "./{datset_name}_tasks/"

    """
    with open("{}_tasks.json".format(dataset_name)) as f:
        tasks = json.load(f)

    tracks_dir = "{}_tracks".format(dataset_name)

    if not os.path.exists(tracks_dir):
        os.mkdir(tracks_dir)

    sources = ["gs://gfw-crowd/{mmsi}_{year}_{month}.json".format(**t['info']) for t in tasks]

    command = ['gsutil', '-m', 'cp', '-n'] + sources + [tracks_dir]

    subprocess.check_output(command)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Download PyBossa data')
    parser.add_argument('project', default="id_fishing_points", nargs='?',
                        help="project name")
    args = parser.parse_args()
    print(download_tracks(args.project).decode('utf8'))