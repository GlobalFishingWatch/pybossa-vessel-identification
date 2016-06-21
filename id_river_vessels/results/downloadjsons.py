#! /usr/bin/python
import urllib2
import json



task_ids = []

with open('id_river_vessels_task 5.json') as data_file:    
    data = json.load(data_file)
    for d in data:
        task_ids.append(d['id'])

print task_ids

for t in task_ids:
    response = urllib2.urlopen('http://crowd.globalfishingwatch.org/api/taskrun?task_id='+str(t))
    html = response.read()
    f = open("jsons/"+str(t)+".json", 'w')
    f.write(html)
    f.close()
	start = 1    
