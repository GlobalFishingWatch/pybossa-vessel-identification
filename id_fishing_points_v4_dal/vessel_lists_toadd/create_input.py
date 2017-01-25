import csv


mmsis = {}
tasks = {}

with open('FishingVesselsV1.csv', 'rU') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        mmsis[row['mmsi']] = row['student_label']

with open('map_tasks_20160224.csv', 'rU') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        mmsi = row['mmsi']
        if mmsi in mmsis:
            print mmsi
            tasks[mmsi] = {}
            months_2014 = row['months_2014'].split(",")
            months_2015 = row['months_2015'].split(",")
            tasks[mmsi]['2014'] = months_2014
            tasks[mmsi]['2015'] = months_2015


with open('tasks_months.csv', 'rU') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        mmsi = row['mmsi']
        if mmsi in mmsis:
            print mmsi
            tasks[mmsi] = {}
            months_2014 = row['months_2014'].split(",")
            months_2015 = row['months_2015'].split(",")
            tasks[mmsi]['2014'] = months_2014
            tasks[mmsi]['2015'] = months_2015

rows = []
for t in tasks:
    for m in tasks[t]['2014']:
        row.append([t,'2014',m, mmsis[t]])
    for m in tasks[t]['2015']:
        rows.append([t,'2015',m, mmsis[t]])


with open('map_tasks_20160512.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(["mmsi","year","month","vesselType"])
    writer.writerows(rows)




