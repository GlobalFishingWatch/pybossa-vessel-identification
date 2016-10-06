from __future__ import print_function
import numpy as np
import pandas as pd
import numpy.lib.recfunctions as rec
import logging


TOLERANCE = 0.001
CHECKS = 10000

for kind in ["trawler", "purse_seine", "longliner"]:
    print("Checking:", kind)
    npz = np.load("id_fishing_points_{}_classified_tracks.npz".format(kind))["x"]
    npz.sort(order=['mmsi', 'timestamp'])
    df = pd.read_csv("id_fishing_points_{}_combined.csv".format(kind))
    selections = np.random.choice(np.arange(len(df)), size=CHECKS, replace=False)
    passed = 0
    failed = 0
    skipped = 0
    for i in selections:
        if df.classification[i] in [-1, 2]:
            continue
        subset = npz[npz['mmsi'] == df.mmsi[i]]
        if not len(subset):
            continue
        j = np.searchsorted(subset['timestamp'], df.timestamp[i])
        if df.timestamp[i] != subset['timestamp'][j]:
            skipped += 1
            continue
        if abs(df.classification[i] - subset['classification'][j]) < TOLERANCE:
            passed += 1
        else:
            failed += 1
    print("Passed:", passed)
    # Some of original PyBossa data has holes in it, so it is possible for
    # there to be points in the range based join that aren't in the 
    # point based join.
    print("Skipped:", skipped)
    print("Failed:", failed)
    if failed:
        print("CHECK FAILED!")
