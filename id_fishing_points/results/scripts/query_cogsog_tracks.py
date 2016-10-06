import sys
import json
import subprocess

dataset_name = sys.argv[1]

with open("%s_tasks.json" % dataset_name) as f:
    mmsis = set((task["info"]["mmsi"] for task in json.load(f)))

query = """
SELECT
  lat, lon, speed, course, mmsi, timestamp
FROM
  TABLE_DATE_RANGE([pipeline_normalize.], TIMESTAMP('2015-01-01'), TIMESTAMP('2015-12-31')) 
where
  mmsi in ({0})
  and lat is not null
  and lon is not null
  and timestamp is not null
  and speed is not null
  and lat<90 and lat>-90 and lon<180 and lon>-180 and lon !=0 and lat !=0
order by
  mmsi, timestamp
""".format(",".join(mmsis))

print(query)

# print(subprocess.check_call(["bq", "query", query]))










# if __name__ == "__main__":
#     import argparse
    
