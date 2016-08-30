import curl
import json
import sys
import os

dataset_name = sys.argv[1]

with open("%s_tasks.json" % dataset_name) as f:
    tasks = json.load(f)

tracks_dir = "%s_tracks" % dataset_name

if not os.path.exists(tracks_dir):
    os.mkdir(tracks_dir)

for idx, task in enumerate(tasks):
    filename = "%(mmsi)s_%(year)s_%(month)s.json" % task["info"]
    print "%s of %s: %s" % (idx, len(tasks), filename),
    outpath = "%s/%s" % (tracks_dir, filename)
    if not os.path.exists(outpath):
        print 'downloading'
        with open(outpath, "w") as f:
            f.write(curl.Curl().get("http://storage.googleapis.com/gfw-crowd/%s" % filename))
    else:
        print 'pre-existing'
