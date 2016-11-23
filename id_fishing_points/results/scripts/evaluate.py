"""Evaluate how closely users agree on rating points as fishing or nonfishing

For example:

    python scripts/evaluate.py \
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


def inferred_accuracy(agreement):
    """Convert agreement to an equivalent accuracy

    Args:
        agreement: float
            Fraction of pairs of raters who agree with each other. 
            In range [0, 1]

    Returns:
        accuracy: float

    Note that this doesn't return the REAL accuracy in terms of fishing / non-fishing,
    rather it assumes that there is some standard that all the raters are trying to 
    meet (transiting / non-fishing or such) and tries to infer how accuracte
    individual rating are by examing how ofter different raters agree.

    Assuming that the raters return the true correct answer with a 
    a probability `alpha` (the accuracy) then `a` (the agreement)
    can be determined by:
    ```
        a = alpha * alpha + (1 - alpha) * (1 - alpha)
    ```
    In other words the agreement is the fraction of the time both
    raters are correct plus the fraction of the time both raters
    are wrong. This leads to:
    ```
        a = 1 - 2 * alpha + 2 * alpha ** 2 
        => (1 - a) - 2 * alpha + 2 * alpha ** 2 = 0
        => alpha = (2 +- sqrt(4 - 8 * (1 - a)) / 4
                 = 0.5 * (1 + sqrt(1 - 2 * (1 - a)))  # Assume accuracy > 0.5
                 ~ 0.5 * (1 + 1 - (1 - a))            # for (1 - a) << 1
                 = 1 - (1 - a) / 2
    ```
    We use the exact formula here, but the final formula is of interest in that it shows
    that the `error` (`1 - alpha`) is half the `disagreement` (`1 - a`).

    """
    return 0.5 * (1 + np.sqrt(1 - 2 * (1 - agreement)))


def compare_users(dataset_name, n_worst, class_map, ignore_ties):

    with open("%s_tasks.json" % dataset_name) as f:
        tasks = {task["id"]: task for task in json.load(f)}

    with open("%s_task_runs.json" % dataset_name) as f:
        task_runs = {task_run["id"]: task_run for task_run in json.load(f)}

    ranges = []

    tasks_examined = 0

    std_dev_map = defaultdict(list)

    gear_map = {}
    all_mmsi = set()
    task_count = 0
    total_used_points = 0
    total_classified_points = 0
    total_points = 0
    ties = 0

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

        if len(task_task_runs) < 2:
            # Only look at tasks that at least two people have looked at
            continue

        task_count += 1

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

        if not values:
            continue

        values = np.transpose(values)
        #
        all_mmsi.add(task["info"]["mmsi"])
        # Standardize on -1 as missing
        values[values == 2] = -1
        total_points += len(values)
        #
        how_many_classified = (values != -1).sum(axis=1)
        total_classified_points += (how_many_classified >= 1).sum()
        # Remove all points that were not classified by at least two people
        enough_ratings = (how_many_classified >= 2)
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

        # Also compute the agreement. We compute the number of pairs that agree as well as the number of
        # total pairs. We then compute the overall agreement, by dividing these later on.

        values[isnan] = 0
        max_count = values.shape[1]
        a = values.sum(axis=1)
        b = (n - a)
        # Pairwise agreement
        agreement = a * (a - 1) + b * (b - 1)
        pairs = n * (n - 1.0)
        if args.ignore_ties:
            # Throw out values with complete disagreement
            # This is to match what we do on extract
            mask = (agreement / pairs != 0.5)
            ties += len(mask) - mask.sum()
            a = a[mask]
            b = b[mask]
            n = n[mask]
            agreement = agreement[mask]
            pairs = pairs[mask]
        total_used_points += len(a)
        # Consensus agreement  
        consensus = np.where(a > b, a, b)
        # We consider it a consensus if more than half of the raters agree
        # when removing the current value. So 2-0 => 1.0, 1-1 => 0, 3-3 => 0, 2-1 => 0, 3-1 => 0.75, etc.
        has_consenseus = np.where((consensus - 1 / n) > 0.5, 1, 0)
        consensus_aggr = np.where(has_consenseus, (consensus / n), 0)
        assert np.all(a <= n), (a, b, n)

        pairs_count = pairs.sum() if len(pairs) else 0
        avg_agreement = agreement.sum() / pairs_count if pairs_count else 0
        avg_cons_aggr = consensus_aggr.mean() if len(consensus_aggr) else 0


        #
        std_dev_map[task["info"]["mmsi"]].append((avg_std_dev, avg_agreement, avg_cons_aggr, len(std_devs), pairs_count))

        #
    std_dev_for_mmsi = {}
    agreement_for_mmsi = {}
    cons_aggreement_for_mmsi = {}
    count_for_mmsi = {}
    pairs_count_for_mmsi = {}
    for m in std_dev_map:
        total_std = 0
        total_agr = 0
        total_cons = 0
        count = 0
        pairs_count = 0
        for std, agr, cons, cnt, pcnt in std_dev_map[m]:
            total_std += cnt * std
            total_agr += pcnt * agr
            total_cons += cnt * cons
            pairs_count += pcnt
            count += cnt
        if count:
            std_dev_for_mmsi[m] = total_std / count
            agreement_for_mmsi[m] = total_agr / pairs_count
            cons_aggreement_for_mmsi[m] = total_cons / count
            count_for_mmsi[m] = count
            pairs_count_for_mmsi[m] = pairs_count
        #

    mmsi = sorted(std_dev_for_mmsi, key=lambda x: std_dev_for_mmsi[x])

    if n_worst:
        print(n_worst, "worst MMSI by StdDev")
        for m in mmsi[-n_worst:]:
            print(m, std_dev_for_mmsi[m], agreement_for_mmsi[m], gear_map[m])
        print()

    print("Total number of Tasks with enough raters", task_count)
    print("Total number of Tasks", len(tasks))
    print("Total number of MMSI processed", len(all_mmsi))
    print("Total number of MMSI processed by more than one person", len(agreement_for_mmsi))
    print("Total classified points {} out of {} total points ({:.2f}%)".format(
        total_classified_points, total_points, 100 * total_classified_points / total_points))
    print("Total number of points used {} out of {} total points  ({:.2f}%)".format(
        total_used_points, total_points, 100 * total_used_points / total_points))
    if ignore_ties:
        print("Total number of ties ignored {} out of {} total points  ({:.2f}%)".format(
            total_used_points, total_points, 100 * ties / total_points))
    print()
    # print("Mean stddev over MMSI: ", np.mean(std_dev_for_mmsi.values()))
    count = 0
    pairs_count = 0
    total_aggr = 0
    total_cons_aggr = 0
    total_stddev = 0
    for m in agreement_for_mmsi:
        total_aggr += pairs_count_for_mmsi[m] * agreement_for_mmsi[m]
        total_cons_aggr += count_for_mmsi[m] * cons_aggreement_for_mmsi[m]
        total_stddev += count_for_mmsi[m] * std_dev_for_mmsi[m]

        count += count_for_mmsi[m]
        pairs_count += pairs_count_for_mmsi[m]

    agreement = total_aggr / pairs_count
    print("Pairwise agreement over all MMSI", agreement)
    print("Inferred accuracy over all MMSI", inferred_accuracy(agreement))
    print("Consensus agreement over all MMSI", total_cons_aggr / count)
    print("Standard Deviationn over all MMSI", total_stddev / count)
    print()

    for cls in np.unique(class_map.values()):
        count = 0
        pairs_count = 0
        total_aggr = 0
        total_cons = 0
        total_std = 0
        for m in agreement_for_mmsi:
            if class_map.get(int(m)) == cls:
                total_aggr += pairs_count_for_mmsi[m] * agreement_for_mmsi[m]
                total_cons += count_for_mmsi[m] * cons_aggreement_for_mmsi[m]
                total_std += count_for_mmsi[m] * std_dev_for_mmsi[m]
                count += count_for_mmsi[m]
                pairs_count += pairs_count_for_mmsi[m]
        if count:
            agreement = total_aggr / pairs_count
            print("Pairwise agreement for", cls, agreement)
            print("Inferred accuracy for", cls, inferred_accuracy(agreement))
            print("Consensus agreement for", cls, total_cons / count)
            print("Standard Deviation for", cls, total_std / count)
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
    parser.add_argument(
        '--ignore-ties', action='store_true', help='ignore tied classifications to match extracted data')
    args = parser.parse_args()
    #

    if args.download:
        download_tracks.download_tracks(args.project)
    with open(args.classes) as f:
        reader =  csv.DictReader(f) 
        class_map = {float(x['mmsi']): x['label'] for x in reader if x['label']}

    compare_users(args.project, args.worst, class_map, args.ignore_ties)
