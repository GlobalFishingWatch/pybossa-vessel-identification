
from __future__ import print_function
from __future__ import division
import ujson as json
import sys
import csv
import datetime
import numpy as np
import numpy.lib.recfunctions as rec
import pandas as pd
import logging


import numpy as np
import dateutil

def is_sorted(x):
    last = x[0]
    for this in x[1:]:
        if this < last:
            return False
        last = this
    return True



def create_fishing_series(mmsi, times, ranges):
    """

    Parameters
    ==========
    mmsi : str

    times : sequence of datetime
        Sequence must be sorted

    ranges: sequence of (mmsi, start_time, end_time, is_fishing)
        mmsi : str
        start_time : str in ISO 8601 format
        stop_time : str in ISO 8601 format
        is_fishing : boolean

    Returns
    =======
    sequence of {[0-1], -1}
        odds of the vessel is fishing at given point or -1 for
        don't know

    """
    if not is_sorted(times):
        raise ValueError("times must be sorted")
    # Only look at ranges associated with the current mmsi
    ranges = ranges[ranges['mmsi'] == mmsi]
    # Initialize is_fishing to -1 (don't know)
    is_fishing = np.zeros([len(times)], dtype=float) # XXX put back into original
    is_fishing_weight = np.zeros([len(times)], dtype=float)
    #
    for _, (_, startstr, endstr, state) in ranges.iterrows():
        start = dateutil.parser.parse(startstr)
        end = dateutil.parser.parse(endstr)
        i0 = np.searchsorted(times, start, side="left")
        i1 = np.searchsorted(times, end, side="right")
        assert 0 <= state <= 1
        is_fishing[i0: i1] += state
        is_fishing_weight[i0:i1] += 1
    mask = (is_fishing_weight > 0)
    is_fishing[mask] /= is_fishing_weight[mask]
    is_fishing[~mask] = -1
    #
    return is_fishing





def merge_all(dataset_name):
    # Create mapping between mmsi and vessel types
    vtype_map = {}
    with open("%s_tasks.json" % dataset_name) as f:
        for task in json.load(f):
            mmsi = int(task['info']['mmsi'])
            vtype = task["info"]["vesselType"].lower()
            if mmsi in vtype_map and vtype_map[mmsi] != vtype:
                logging.warn("{} already in vtype_map with different vtype".format(mmsi))
            vtype_map[mmsi] = vtype
    #
    tracks_npz = np.load("%s_cogsog_tracks.npz" % dataset_name)["arr_0"]
    tracks_map = {x : tracks_npz[x] for x in tracks_npz.dtype.names}
    tracks = pd.DataFrame(tracks_map)
    tracks['classification'] = [-1] * len(tracks)
    classification = -1 * np.ones([len(tracks)], dtype=float)
    ranges = pd.read_csv("{}_ranges.csv".format(dataset_name))
    mmsi = sorted(set([int(x) for x in tracks['mmsi']]))
    mmsi_chunks = []
    time_chunks = []
    state_chunks = []
    track_mmsi = np.array([int(x) for x in tracks['mmsi']])
    for m in mmsi: 
        logging.info("processing MMSI: {}".format(m))
        mask = (track_mmsi == m)
        timestamps = tracks.timestamp[mask]
        times = pd.to_datetime(timestamps, unit='s')
        indices = np.argsort(times.values)
        times = [times.iloc[i] for i in indices]
        states = create_fishing_series(m, times, ranges)
        permuted_states = np.zeros_like(states)
        permuted_states[indices] = states
        classification[mask] = permuted_states
    tracks["classification"] = classification
    # Dont' return unclassified tracks
    valid_tracks = (tracks.classification != -1)
    #
    for vtype in sorted(set(vtype_map.values())):
        logging.info("dumping vessel type: {}".format(vtype))
        mask = np.zeros([len(tracks)], dtype=bool)
        for mmsi in vtype_map:
            if vtype_map[mmsi] != vtype:
                continue
            mask |= (track_mmsi == mmsi)
        mask &= valid_tracks
        print("Lengths", len(mask), mask.sum(), len(tracks[mask]))
        print((tracks[mask].classification < 0).sum(), (tracks[mask].classification > 1).sum())
        tracks[mask].to_csv("{}_{}_combined.csv".format(dataset_name, vtype))





if __name__ == "__main__":
    import argparse
    logging.getLogger().setLevel("INFO")
    parser = argparse.ArgumentParser(description='Merge range data with track data')
    parser.add_argument('project', default="id_fishing_points", nargs='?',
                        help="project name")
    args = parser.parse_args()
    merge_all(args.project)
