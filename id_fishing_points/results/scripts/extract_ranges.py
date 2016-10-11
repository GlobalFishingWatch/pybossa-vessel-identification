from __future__ import division
import ujson as json
import sys
import csv
import datetime
import numpy as np
import numpy.lib.recfunctions as rec
import logging
from mussidae import time_range_tools as trtools
import download_tracks


def extract_ranges(dataset_name):

    with open("%s_tasks.json" % dataset_name) as f:
        tasks = {task["id"]:task for task in json.load(f)}

    with open("%s_task_runs.json" % dataset_name) as f:
        task_runs = {task_run["id"]:task_run for task_run in json.load(f)}

    ranges = []

    for tidx, task in enumerate(tasks.values()):
        track_filename = "%(mmsi)s_%(year)s_%(month)s.json" % task["info"]

        logging.info("Task %s of %s: %s" % (tidx, len(tasks), track_filename))

        try:
            with open("%s_tracks/%s" % (dataset_name, track_filename)) as f:
                track = json.load(f)
        except Exception as e:
            logging.warning('could not load {} ({})'.format(track_filename, repr(e)))
            continue

        classifications = []
        total_confidence = []

        task_task_runs = [task_run for task_run in task_runs.values() if task_run["task_id"] == task["id"]]

        for tridx, task_run in enumerate(task_task_runs):
            logging.info("    Run %s of %s: %s" % (tridx, len(task_task_runs), task_run['id']))
            try:
                run_info = json.loads(task_run["info"])
            except Exception as e:
                logging.warning('could not load run {}\n{}'.format(tridx, repr(e)))
                continue

            if run_info["confidence"] == "no_confidence": 
                continue

            if len(run_info["fishingArrayString"]) != len(track["timestamps"]):
                logging.warning("bad length, clipping (%s != %s)" % (len(run_info["fishingArrayString"]), len(track["timestamps"])))
                run_info["fishingArrayString"] = run_info["fishingArrayString"][:len(track["timestamps"])]
                continue

            is_fishing = np.array([float(x) for x in run_info["fishingArrayString"]])
            if np.sometrue(((is_fishing < 0) | (is_fishing > 1)) & (is_fishing != 2)):
                print("values out of range, skipping", sorted(set(is_fishing)))
                continue

            confidence = {
                "low_confidence": 0.5,
                "medium_confidence": 0.75,
                "high_confidence": 1.0
                }[run_info["confidence"]]

            if not classifications:
                classifications = [0.0] * len(run_info["fishingArrayString"])
                total_confidence = [0.0] * len(run_info["fishingArrayString"])

            for idx, isf in enumerate(is_fishing):
                if isf != 2: # 2 is "don't know"
                    classifications[idx] += isf * confidence
                    total_confidence[idx] += confidence

        if not classifications:
            continue

        mmsi = [task["info"]["mmsi"]] * len(classifications)
        states = [(c / t if t else -1) for (c, t) in zip(classifications, total_confidence)]

        times = [trtools.parse_timestamp(ts) for ts in track["timestamps"]]


        points = [trtools.Point(*args) for args in zip(mmsi, times, states)]

        for _, _, s in points:
            assert 0 <= s <= 1 or s == -1

        ranges.extend(trtools.ranges_from_points(points))

    return ranges







if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Extract fishing/nonfishing ranges from PyBossa data')
    parser.add_argument('project', default="id_fishing_points", nargs='?',
                        help="project name")
    parser.add_argument('--download', action="store_true",
                        help="download track data")
    args = parser.parse_args()
    #
    if args.download:
        download_tracks.download_tracks(args.project)
    ranges = extract_ranges(args.project)
    trtools.write_ranges(ranges, "{}_ranges.csv".format(args.project))

