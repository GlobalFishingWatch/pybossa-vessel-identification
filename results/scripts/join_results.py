import curl
import ujson as json
import sys
import csv
import datetime
import numpy as np
import numpy.lib.recfunctions as rec

dataset_name = sys.argv[1]

with open("%s_tasks.json" % dataset_name) as f:
    tasks = {task["id"]:task for task in json.load(f)}

with open("%s_task_runs.json" % dataset_name) as f:
    task_runs = {task_run["id"]:task_run for task_run in json.load(f)}

cogsogtracks = np.load("%s_cogsog_tracks.npz" % dataset_name)["arr_0"]

res = None

for tidx, task in enumerate(tasks.itervalues()):
    track_filename = "%(mmsi)s_%(year)s_%(month)s.json" % task["info"]

    print "Task %s of %s: %s" % (tidx, len(tasks), track_filename)

    try:
        with open("%s_tracks/%s" % (dataset_name, track_filename)) as f:
            track = json.load(f)
    except Exception, e:
        print e
        continue

    classifications = []
    total_confidence = 0

    task_task_runs = [task_run for task_run in task_runs.itervalues() if task_run["task_id"] == task["id"]]

    for tridx, task_run in enumerate(task_task_runs):
        print "    Run %s of %s: %s" % (tridx, len(task_task_runs), task_run['id'])
        try:
            run_info = json.loads(task_run["info"])
        except Exception, e:
            print e
            continue

        if run_info["confidence"] == "no_confidence": continue

        if len(run_info["fishingArrayString"]) != len(track["timestamps"]):
            print "        BAD LENGTH %s != %s" % (len(run_info["fishingArrayString"]), len(track["timestamps"]))
            continue

        confidence = {
            "low_confidence": 0.5,
            "medium_confidence": 0.75,
            "high_confidence": 1.0
            }[run_info["confidence"]]
        total_confidence += confidence

        if not classifications:
            classifications = [0.0] * len(run_info["fishingArrayString"])

        for idx in xrange(0, len(run_info["fishingArrayString"])):
            classifications[idx] += float(run_info["fishingArrayString"][idx]) * confidence
    classifications = [classification / total_confidence for classification in classifications]

    if not classifications:
        continue

    classified_track = np.zeros(len(track["timestamps"]), dtype=[("timestamp", "float"), ("lat", "float"), ("lon", "float"), ("classification", "float")])

    classified_track["timestamp"][:] = [(datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") - datetime.datetime(1970, 1, 1)).total_seconds()
                                        for timestamp in track["timestamps"]]
    classified_track["lat"][:] = track["lats"]
    classified_track["lon"][:] = track["lons"]
    classified_track["classification"][:] = classifications

    cogsogtrack = cogsogtracks[cogsogtracks["mmsi"] == float(task["info"]["mmsi"])]

    classified_cogsogtrack = rec.join_by(["timestamp"], classified_track, cogsogtrack, "leftouter")
    classified_cogsogtrack = classified_cogsogtrack[classified_cogsogtrack.mask["lat1"] == False]

    classified_cogsogtrack = rec.drop_fields(classified_cogsogtrack, ["lat1", "lon1"])
    classified_cogsogtrack = rec.rename_fields(classified_cogsogtrack, {"lon2": "lon", "lat2": "lat"})

    if res is None:
        res = classified_cogsogtrack
    else:
        res = np.append(res, classified_cogsogtrack)

np.savez("%s_classified_tracks.npz" % dataset_name, x=res)
