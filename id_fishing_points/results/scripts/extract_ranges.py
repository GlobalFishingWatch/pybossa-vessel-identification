from __future__ import division
import ujson as json
import sys
import csv
import datetime
import numpy as np
import numpy.lib.recfunctions as rec
import logging


# From vessel scoring currently, but moving to mussidae. import from there
# when relocated
def dedup_and_sort_points(points):
    points.sort()
    dedupped = []
    last_key = (None, None)
    last_fishing = None
    for mmsi, timestamp, is_fishing in points:
        key = (mmsi, timestamp)
        is_fishing = None if is_fishing in (-1, 2) else is_fishing
        if key == last_key:
            if is_fishing != last_fishing:
                dedupped[-1] = (mmsi, timestamp, None)
        else:
            dedupped.append((mmsi, timestamp, is_fishing))
            last_key = key
            last_fishing = is_fishing

    return dedupped


def ranges_from_points(points):
    points = dedup_and_sort_points(points)
    current_state = None
    current_mmsi = None
    ranges = []
    for mmsi, time, state in points:
        if mmsi != current_mmsi or state != current_state:
            if current_state is not None:
                ranges.append((current_mmsi, range_start.isoformat(), last_time.isoformat(), current_state))
            current_state = state
            range_start = time
            current_mmsi = mmsi
        last_time = time
    if current_state is not None:
        ranges.append((current_mmsi, range_start.isoformat(), last_time.isoformat(), current_state))
    return ranges


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
            logging.warning('could not load {}\n{}'.format(track_filename, repr(e)))
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
                logging.warning("        BAD LENGTH %s != %s" % (len(run_info["fishingArrayString"]), len(track["timestamps"])))
                logging.warning("clipping")
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

        times = [datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in track["timestamps"]]


        points = list(zip(mmsi, times, states))

        for _, _, s in points:
            assert 0 <= s <= 1 or s == -1

        ranges.extend(ranges_from_points(points))

    return ranges







if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Extract fishing/nonfishing ranges from PyBossa data')
    parser.add_argument('project', default="id_fishing_points", nargs='?',
                        help="project name")
    args = parser.parse_args()
    results = extract_ranges(args.project)

    with open("{}_ranges.csv".format(args.project), 'w') as f:
        f.write("mmsi,start_time,end_time,is_fishing\n")
        for row in results:
            f.write("{}\n".format(','.join(str(x) for x in row)))

