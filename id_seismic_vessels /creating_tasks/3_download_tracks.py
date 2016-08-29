from datetime import datetime
import json
import subprocess
import os
import csv
import matplotlib.pyplot as plt


today_date = "20160715"

out_dir = '../../data/vessels_'+today_date+'/'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

path_to_table_dir = "../../data/bigquery_tables/"
table = "vessels_"+today_date

mmsi_year_months = []
tasks = []

import gzip
with gzip.open(path_to_table_dir+table+".zip", 'rb') as f:
    reader = csv.DictReader(f)
    lats = []
    lons = []
    sogs = []
    timestamps = []
    for row in reader:

        # check to see if there is a new mmsi
        mmsi = row['mmsi']
        t = row['timestamp']
        timestamp = datetime.strptime(t, "%Y-%m-%d %H:%M:%S UTC")
        y = timestamp.year 
        m = timestamp.month 
        mmsi_year_month = str(mmsi)+str(y)+str(m)
        if len(mmsi)>0 and mmsi_year_month not in mmsi_year_months:
            mmsi_year_months.append(mmsi_year_month)
            if len(lats)>100: #has to have at least 100 positions in the month
                js = {}
                js['lats']=lats
                js['lons']=lons
                js['sogs']=sogs
                js['timestamps']=[str(t) for t in timestamps] # turn back into string for json ojbect   
                y = timestamps[0].year 
                m = timestamps[0].month
                t = json.dumps(js)
                json_path = "../../data/vessels_"+today_date+"/"
                json_filename = filename = str(last_mmsi)+"_"+str(y)+"_"+str(m)+".json"
                f = open(json_path + json_filename,'w')
                f.write(t)
                f.close()

                # upload to gcs and set the permissions to be public
                subprocess.call("gsutil -m cp "+ json_path + json_filename +" gs://gfw-crowd/"+json_filename+\
                    ";gsutil -m acl set -R -a public-read gs://gfw-crowd/"+json_filename,shell = True)
                # add to the tasks
                tasks.append((mmsi,2015,m))

            # reset the values to nothing
            lats = []
            lons = []
            sogs = []
            timestamps = []

        lat = round(float(row['lat']),5)
        lon = round(float(row['lon']),5)
        sog = round(float(row['speed']),1)
        last_mmsi = row['mmsi']
        sogs.append(sog)
        lats.append(lat)
        lons.append(lon)
        timestamps.append(timestamp)



# now make the histograms

def make_histogram(mmsi, sogs):

    sogs2 = []
    for s in sogs:
        if s>0.1 and s<30:
            sogs2.append(s)

    if len(sogs2)>5:
        plt.hist(sogs2,bins=40)
        plt.title("Speed distribution for vessel "+str(mmsi))
        plt.xlabel("Speed, Knots")
        plt.ylabel("Frequency")
        fig = plt.gcf()
        fig_size = plt.rcParams["figure.figsize"]
     
        # set figure width and height
        fig_size[0] = 9
        fig_size[1] = 2.5
        plt.rcParams["figure.figsize"] = fig_size    
        plt.gcf().subplots_adjust(bottom=0.20)
        fig.set_size_inches(fig_size[0] , fig_size[1] )
        histogram_filename = str(mmsi)+'.png'
        fig.savefig(outdir_histograms+ histogram_filename, dpi=100, bbox_inches='tight')
        command = "gsutil -m cp "+ outdir_histograms+ histogram_filename +" gs://gfw-crowd/histogram/"+histogram_filename + \
            ";gsutil -m acl set -R -a public-read gs://gfw-crowd/histogram/"+histogram_filename
        # upload to gcs and set the permissions to be public
        print command
        subprocess.call(command, shell = True)
        plt.clf()
    else:
        print "not enough data for ",mmsi," to make a speed histogram"




outdir_histograms = '../../data/vessel_histograms_'+today_date+'/'
if not os.path.exists(outdir_histograms):
    os.makedirs(outdir_histograms)

mmsis = {}
for t in tasks:
    if t[0] not in mmsis:
        mmsis[t[0]] = []
    mmsis[t[0]].append(t[2])

year = 2015
for mmsi in mmsis:
    sogs = []
    for m in mmsis[mmsi]:
        try:
            filename = out_dir+str(mmsi)+"_"+str(year)+"_"+str(m)+".json"
            f = open(filename,'rU')
            sogs += json.loads(f.read())['sogs']
            f.close()
        except Exception as e:
            print filename, e
    make_histogram(mmsi, sogs)


# # tasks are in the wrong format

# print tasks
tasks2 = []
for m in mmsis:
    mmsi_list = []
    for mmsi in mmsis[m]:
        mmsi_list.append(str(mmsi))
    tasks2.append(m, ",".join(mmsi_list))

# now create the task infile
with open("../tasks_"+today_date+".csv", 'wb') as f:
    writer = csv.writer(f)
    theheader = ['mmsi','months_2015']
    writer.writerow(theheader) 
    writer.writerows(tasks2)




