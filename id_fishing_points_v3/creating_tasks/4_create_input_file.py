from os import listdir
from os.path import isfile, join
import random
from operator import itemgetter
import csv

today_date = "20160612"
mypath = "../../data/vessels_"+today_date+"/"
mypath = "../../data/vessels_"+today_date+"/"
files = [f.replace(".json","") for f in listdir(mypath) if isfile(join(mypath, f)) and ".json" in f]


vessels = []
mmsi_types = {}
output_type = {'Longliners':'longliner', 'Trawlers':'trawler','Purse Seiners':'purse_seine'}

with open("to_classify_fishing_160612.csv", "rU") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        vessels.append(row['mmsi']) 
        mmsi_types[row['mmsi']] = output_type[row['shiptype']]

tasks = []
for f in files:
	row =  f.split("_")
	row.append(mmsi_types[row[0]])
	tasks.append(row)

sorted(tasks)

with open("../tasks_"+today_date+".csv", 'wb') as f:
    writer = csv.writer(f)
    theheader = ['mmsi','year','month','vesselType']
    writer.writerow(theheader) 
    writer.writerows(tasks)
