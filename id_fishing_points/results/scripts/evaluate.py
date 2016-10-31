"""Evaluate how closely users agree on rating points as fishing or nonfishing

For example:

    python scripts/compare_users.py \
         --classes ../../../mussidae/mussidae/data-precursors/time-range-sources/non-public-sources/mmsi_to_vessel_type.csv \
         id_fishing_points_3




"""

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

def compare_users(dataset_name, n_worst, class_map):

    with open("%s_tasks.json" % dataset_name) as f:
        tasks = {task["id"]: task for task in json.load(f)}

    with open("%s_task_runs.json" % dataset_name) as f:
        task_runs = {task_run["id"]: task_run for task_run in json.load(f)}

    ranges = []

    tasks_examined = 0

    std_dev_map = defaultdict(list)

    gear_map = {}
    all_mmsi = set()


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
        #
        all_mmsi.add(task["info"]["mmsi"])
        # Standardize on -1 as missing
        values[values == 2] = -1
        # Remove all points that were not classified by at least two people
        enough_ratings = ((values != -1).sum(axis=1) >= 2)
        #
        #
        values = values[enough_ratings]
        assert np.all((values == -1) | (values == 0) | (values == 1))

        values[values == -1] = np.nan
        isnan = np.isnan(values)
        mask = ~isnan
        n = mask.sum(axis=1)
        std_devs = np.nanstd(values, axis=1) * n / (n - 1)
        #
        avg_std_dev = std_devs.mean() if len(std_devs) else 0

        # Also compute the agreement. Agreement with more than 2 people is computed as
        # the fraction of all possible pairs that agree == a * (a - 1) / (n * (n - 1))

        values[isnan] = 0
        max_count = values.shape[1]
        a = values.sum(axis=1)
        b = (n - a)
        # Pairwise agreement
        agreement = (a * (a - 1) + b * (b - 1)) / (n * (n - 1.0)) 
        # Consensus agreement  
        consensus = np.where(a > b, a, b)
        # We consider it a consensus if more than half of the raters agree
        # when removing the current value. So 2-0 => 1.0, 1-1 => 0, 3-3 => 0, 2-1 => 0, 3-1 => 0.75, etc.
        has_consenseus = np.where((consensus - 1 / n) > 0.5, 1, 0)
        consensus_aggr = np.where(has_consenseus, (consensus / n), 0)
        assert np.all(a <= n), (a, b, n)

        avg_agreement = agreement.mean() if len(agreement) else 0
        avg_cons_aggr = consensus_aggr.mean() if len(consensus_aggr) else 0


        #
        std_dev_map[task["info"]["mmsi"]].append((avg_std_dev, avg_agreement, avg_cons_aggr, len(std_devs)))

        #
    std_dev_for_mmsi = {}
    agreement_for_mmsi = {}
    cons_aggreement_for_mmsi = {}
    count_for_mmsi = {}
    for m in std_dev_map:
        total_std = 0
        total_agr = 0
        total_cons = 0
        count = 0
        for std, agr, cons, cnt in std_dev_map[m]:
            total_std += cnt * std
            total_agr += cnt * agr
            total_cons += cnt * cons
            count += cnt
        if count:
            std_dev_for_mmsi[m] = total_std / count
            agreement_for_mmsi[m] = total_agr / count
            cons_aggreement_for_mmsi[m] = total_cons / count
            count_for_mmsi[m] = count
        #

    mmsi = sorted(std_dev_for_mmsi, key=lambda x: std_dev_for_mmsi[x])

    if n_worst:
        print(n_worst, "worst MMSI by StdDev")
        for m in mmsi[-n_worst:]:
            print(m, std_dev_for_mmsi[m], agreement_for_mmsi[m], gear_map[m])
        print()

    print("Total number of MMSI processed", len(all_mmsi))
    print("Total number of MMSI processed by more than one person", len(agreement_for_mmsi))
    # print("Mean stddev over MMSI: ", np.mean(std_dev_for_mmsi.values()))
    count = 0
    total_aggr = 0
    total_cons_aggr = 0
    total_stddev = 0
    for m in agreement_for_mmsi:
        total_aggr += count_for_mmsi[m] * agreement_for_mmsi[m]
        total_cons_aggr += count_for_mmsi[m] * cons_aggreement_for_mmsi[m]
        total_stddev += count_for_mmsi[m] * std_dev_for_mmsi[m]

        count += count_for_mmsi[m]

    print("Pairwise agreement over all MMSI", total_aggr / count)
    print("Consensus agreement over all MMSI", total_cons_aggr / count)
    print("Standard Deviationn over all MMSI", total_stddev / count)
    print()

    for cls in np.unique(class_map.values()):
        count = 0
        total_aggr = 0
        total_cons = 0
        total_std = 0
        for m in agreement_for_mmsi:
            if class_map.get(int(m)) == cls:
                total_aggr += count_for_mmsi[m] * agreement_for_mmsi[m]
                total_cons += count_for_mmsi[m] * cons_aggreement_for_mmsi[m]
                total_std += count_for_mmsi[m] * std_dev_for_mmsi[m]
                count += count_for_mmsi[m]
        if count:
            print("Pairwise agreement for", cls, total_aggr / count)
            print("Consensus agreement for", cls, total_cons / count)
            print("Standard Deviationn for", cls, total_std / count)
            print()



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Extract fishing/nonfishing ranges from PyBossa data')
    parser.add_argument(
        'project', default="id_fishing_points", nargs='?', help="project name")
    parser.add_argument(
        '--download', action="store_true", help="download track data")
    parser.add_argument(
        '--classes', required=True, help="file mapping mmsi to classes")
    parser.add_argument(
        '--worst', type=int, default=0, help="number of worst MMSI to print")
    args = parser.parse_args()
    #

    if args.download:
        download_tracks.download_tracks(args.project)
    with open(args.classes) as f:
        reader =  csv.DictReader(f) 
        class_map = {float(x['mmsi']): x['label'] for x in reader if x['label']}

    compare_users(args.project, args.worst, class_map)
