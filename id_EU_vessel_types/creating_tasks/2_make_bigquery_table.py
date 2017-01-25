"""
The following script creates a bigtable table with all the tracks of vessels in a
csv file to_classify_ + [string of the date the file was created]

You should only change the variable today_date

The code for downloading a table from BigQuery was writtne by Tim Hochberg:
https://github.com/GlobalFishingWatch/nn-vessel-classification/blob/master/tah-proto/get-data/gctools.py
"""

import uuid
import time
import subprocess
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import csv

# this is the key used to identify all tracks made on a given day
today_date = "20160921"

path_to_table_dir = "../../data/bigquery_tables/"


# the mmsi to be added must be in a csv file with the format to_classify_{today_date}.csv, in a column labeled "mmsi"
mmsis = []
with open("Gear_Types_to_Load_"+today_date+".csv", "rU") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        mmsis.append(row['mmsi'])  

#get all the tracks into a bigquery table
query = '''
SELECT lat, lon, speed, mmsi, timestamp FROM TABLE_DATE_RANGE([pipeline_normalize.], TIMESTAMP('2015-01-01'), TIMESTAMP('2015-12-31')) 
where mmsi in ( '''+ ",".join(mmsis)+ ''' ) and 
lat is not null and lon is not null and timestamp is not null and speed is not null and 
lat<90 and lat>-90 and lon<180 and lon>-180 and lon !=0 and lat !=0
order by mmsi, timestamp
'''

print query

proj_id = "world-fishing-827"
dataset = "scratch_david_vesselsPyBossa"
table = "vessels_"+today_date

class BigQuery:

    def __init__(self):
        credentials = GoogleCredentials.get_application_default()
        self._bq = discovery.build('bigquery', 'v2', credentials=credentials)


    # XXX allow dataset/table to be optional (should probably pass in as atomic `destination`)
    # XXXX allow allowLargeResults to be optional
    # XXX check that dataset/table set if not
    # XXX ADD note that if dest table specified it is not automatically deleted
    def async_query(self, project_id, query, dataset, table,
                        batch=False, num_retries=5):
        """Create an asynchronous BigQuery query
        MOAR DOCS
        """
        # Generate a unique job_id so retries
        # don't accidentally duplicate query
        job_data = {
            'jobReference': {
                'projectId': project_id,
                'job_id': str(uuid.uuid4())
            },
            'configuration': {
                'query': {
                    'allowLargeResults': 'true',
                    'destinationTable' : {
                      "projectId": project_id,
                      "datasetId": dataset,
                      "tableId": table,
                      },
                    'query': query,
                    'priority': 'BATCH' if batch else 'INTERACTIVE'
                }
            }
        }
        return self._bq.jobs().insert(
            projectId=project_id,
            body=job_data).execute(num_retries=num_retries)


    def poll_job(self, job, max_tries=4000):
        """Waits for a job to complete."""

        request = self._bq.jobs().get(
            projectId=job['jobReference']['projectId'],
            jobId=job['jobReference']['jobId'])

        trial = 0
        while trial < max_tries:
            result = request.execute(num_retries=2)

            if result['status']['state'] == 'DONE':
                if 'errorResult' in result['status']:
                    raise RuntimeError(result['status']['errorResult'])
                return

            time.sleep(1)
            trial += 1

        raise RuntimeError("timeout")


    def async_extract_query(self, job, path, format="CSV", compression="GZIP",
                                                        num_retries=5):
        """Extracts query specified by job into Google Cloud storage at path
        MOAR docs
        """

        job_data = {
          'jobReference': {
              'projectId': job['jobReference']['projectId'],
              'jobId': str(uuid.uuid4())
          },
          'configuration': {
              'extract': {
                  'sourceTable': {
                      'projectId': job['configuration']['query']['destinationTable']['projectId'],
                      'datasetId': job['configuration']['query']['destinationTable']['datasetId'],
                      'tableId': job['configuration']['query']['destinationTable']['tableId'],
                  },
                  'destinationUris': [path],
                  'destinationFormat': format,
                  'compression': compression
              }
          }
        }
        return self._bq.jobs().insert(
            projectId=job['jobReference']['projectId'],
            body=job_data).execute(num_retries=num_retries)


def gs_mv(src_path, dest_path):
    """Move data using gsutil
    This was written to move data from cloud
    storage down to your computer and hasn't been
    tested for other things.
    Example:
    gs_mv("gs://world-fishing-827/scratch/SOME_DIR/SOME_FILE",
                "some/local/path/.")
    """
    subprocess.call(["gsutil", "-m", "mv", src_path, dest_path])


gcs_path = "gs://david-scratch/"+table+".zip"
local_path = path_to_table_dir+table+".zip"

bigq = BigQuery()
query_job = bigq.async_query(proj_id, query, dataset, table)
bigq.poll_job(query_job)
extract_job = bigq.async_extract_query(query_job, gcs_path)
bigq.poll_job(extract_job)
gs_mv(gcs_path, local_path)

