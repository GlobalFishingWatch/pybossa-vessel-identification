from os import listdir
from os.path import isfile, join
import random
from operator import itemgetter
import csv

today_date = "20160624"
mypath = "../../data/vessels_"+today_date+"/"
mypath = "../../data/vessels_"+today_date+"/"
files = [f.replace(".json","") for f in listdir(mypath) if isfile(join(mypath, f)) and ".json" in f]


vessels_doubled = [f.split("_")[0] for f in files]
vessels = []
for v in vessels_doubled:
    if v not in vessels:
        vessels.append(v)

tasks = []

for v in vessels:
    selects = []
    selects2 = []
    #v_months[v]=[]
    for f in files:
        if str(v) == f.split("_")[0]:
            m = int(f.split("_")[2])
            y = int(f.split("_")[1])
            if y == 2015:
                selects.append(m)
            if y == 2014:
                selects2.append(m)
    if len(selects)+len(selects2)>2:
        # selects = sorted(selects, key=itemgetter(0))
        selects = sorted(selects)#, key=itemgetter(1))
        selects2 = sorted(selects2)#, key=itemgetter(1))

        for i in range(len(selects)): 
            selects[i]=str(selects[i])
        
        for j in range(len(selects2)): 
            selects2[j]=str(selects2[j])

#        print str(v)+"\t"+",".join(selects2)+"\t"+ (",".join(selects))
        tasks.append([v,",".join(selects)])



with open("../tasks_"+today_date+".csv", 'wb') as f:
    writer = csv.writer(f)
    theheader = ['mmsi','months_2015']
    writer.writerow(theheader) 
    writer.writerows(tasks)
