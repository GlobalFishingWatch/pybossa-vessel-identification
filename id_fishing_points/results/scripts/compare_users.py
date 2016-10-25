from __future__ import division
from __future__ import print_function
import ujson as json
import sys
import csv
import datetime
import numpy as np
import numpy.lib.recfunctions as rec
import logging
from mussidae import time_range_tools as trtools
import download_tracks
from collections import defaultdict

def compare_users(dataset_name, n_worst):

    with open("%s_tasks.json" % dataset_name) as f:
        tasks = {task["id"]: task for task in json.load(f)}

    with open("%s_task_runs.json" % dataset_name) as f:
        task_runs = {task_run["id"]: task_run for task_run in json.load(f)}

    ranges = []

    tasks_examined = 0

    std_dev_map = defaultdict(list)

    gear_map = {}

    for tidx, task in enumerate(tasks.values()):
        gear_map[task['info']['mmsi']] = task['info']['vesselType']

        track_filename = "%(mmsi)s_%(year)s_%(month)s.json" % task["info"]

        logging.info("Task %s of %s: %s" % (tidx, len(tasks), track_filename))

        try:
            with open("%s_tracks/%s" % (dataset_name, track_filename)) as f:
                track = json.load(f)
        except Exception as e:
            logging.warning('could not load {} ({})'.format(track_filename,
                                                            repr(e)))
            continue

        classifications = []
        total_confidence = []

        task_task_runs = [task_run for task_run in task_runs.values()
                          if task_run["task_id"] == task["id"]]

        if len(task_task_runs) < 3:
            # Only look at tasks that at least three people have looked at
            continue

        values = []

        for tridx, task_run in enumerate(task_task_runs):
            logging.info("    Run %s of %s: %s" %
                         (tridx, len(task_task_runs), task_run['id']))
            try:
                run_info = json.loads(task_run["info"])
            except Exception as e:
                logging.warning('could not load run {}\n{}'.format(tridx, repr(
                    e)))
                continue

            if run_info["confidence"] in ("no_confidence", "skip"):
                continue

            if len(run_info["fishingArrayString"]) > len(track["timestamps"]):
                logging.warning("bad length, clipping (%s != %s)" %
                                (len(run_info["fishingArrayString"]),
                                 len(track["timestamps"])))
                run_info["fishingArrayString"] = run_info[
                    "fishingArrayString"][:len(track["timestamps"])]

            is_fishing = np.array(
                [float(x) for x in run_info["fishingArrayString"]])
            if np.sometrue(((is_fishing < 0) | (is_fishing > 1)) & (is_fishing
                                                                    != 2)):
                print("values out of range, skipping", sorted(set(is_fishing)))
                continue

            values.append(is_fishing)

        values = np.transpose(values)
        # Standardize on -1 as missing
        values[values == 2] = -1
        # Remove all points that were not classified by at least two people
        enough_ratings = ((values != -1).sum(axis=1) >= 2)
        #
        #
        values = values[enough_ratings]
        assert np.all((values == -1) | (values == 0) | (values == 1))

        values[values == -1] = np.nan
        std_devs = np.nanstd(values, axis=1)
        #
        avg_std_dev = std_devs.mean() if len(std_devs) else 0

        # Also compute the agreement. Agreement with more than 2 people is computed as
        # the fraction of all possible pairs that agree == a * (a - 1) / (n * (n - 1))
        isnan = np.isnan(values)
        mask = ~isnan
        values[isnan] = 0
        max_count = values.shape[1]
        n = mask.sum(axis=1)
        ones = values.sum(axis=1)
        a = np.where(ones < max_count // 2, n - ones, ones)
        agreement = a * (a - 1) / (n * (n - 1.0))
        assert np.all(a <= n), (a, n, ones)

        avg_agreement = agreement.mean() if len(agreement) else 0

        #
        std_dev_map[task["info"]["mmsi"]].append((avg_std_dev, avg_agreement, len(std_devs)))

        #
    std_dev_for_mmsi = {}
    argreement_for_mmsi = {}
    for m in std_dev_map:
        total_std = 0
        total_agr = 0
        count = 0
        for std, agr, cnt in std_dev_map[m]:
            total_std += cnt * std
            total_agr += cnt * agr
            count += cnt
        if count:
            std_dev_for_mmsi[m] = total_std / count
            argreement_for_mmsi[m] = total_agr / count
        #

    mmsi = sorted(std_dev_for_mmsi, key=lambda x: std_dev_for_mmsi[x])

    if n_worst:
        print(n_worst, "worst MMSI by StdDev")
        for m in mmsi[-n_worst:]:
            print(m, std_dev_for_mmsi[m], argreement_for_mmsi[m], gear_map[m])
        print()

    print("Mean stddev over MMSI: ", np.mean(std_dev_for_mmsi.values()))
    print("Mean agreement over MMSI: ", np.mean(argreement_for_mmsi.values()))




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Extract fishing/nonfishing ranges from PyBossa data')
    parser.add_argument(
        'project', default="id_fishing_points", nargs='?', help="project name")
    parser.add_argument(
        '--download', action="store_true", help="download track data")
    parser.add_argument(
        '--worst', type=int, default=10, help="number of worst MMSI to print")
    args = parser.parse_args()
    #

    if args.download:
        download_tracks.download_tracks(args.project)
    compare_users(args.project, args.worst)
