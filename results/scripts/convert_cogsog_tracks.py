import sys
import datetime
import numpy as np
import numpy.lib.recfunctions as rec

dataset_name = sys.argv[1]

def conv(dt):
    if not dt: return None
    try:
        return (datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S UTC") - datetime.datetime(1970, 1, 1)).total_seconds()
    except Except, e:
        print "%s: %s" % (repr(dt), e)
        return None

cogsogtracks = np.recfromcsv("%s_cogsog_tracks.csv" % dataset_name, delimiter=',', filling_values=np.nan, case_sensitive=True, deletechars='', replace_space=' ')
timestamps = np.zeros(len(cogsogtracks))
timestamps[:] = [conv(t) for t in cogsogtracks["timestamp"]]

cogsogtracks = rec.drop_fields(cogsogtracks, "timestamp")
cogsogtracks = rec.append_fields(cogsogtracks, "timestamp", [], dtypes="f8", fill_value=0.0)
cogsogtracks["timestamp"][:] = timestamps

np.savez("%s_cogsog_tracks.npz" % dataset_name, cogsogtracks.filled())
