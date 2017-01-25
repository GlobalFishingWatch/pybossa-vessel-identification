#! /usr/bin/python
import json
import requests
import time
import sys

'''
Usage
!python download_results.py project_name

This downloads the tasks and task_runs for a given project, and saves them into
json files project_name_tasks.json and project_name_task_runs.json
'''


project_name = sys.argv[1] # 


# first get the project id
project_list = "http://crowd.globalfishingwatch.org/api/project"

res = requests.get(project_list)
projects = json.loads(res.text)

for t in projects:
    if t['short_name']==project_name:
    	project_id = t['id']

# now get the taskruns
taskrun_url = "http://crowd.globalfishingwatch.org/api/taskrun?project_id="+str(project_id)+"&limit=100&offset="

page = 0
results = []
while 1:
	res = requests.get(taskrun_url+str(page*100))
	if int(res.headers['X-RateLimit-Remaining']) < 10:
	    time.sleep(300) # Sleep for 5 minutes
	else:
		j = json.loads(res.text)
		if len(j)==0:
			break
		results = results + j	
		print "downloading " , taskrun_url+str(page*100)		
		page +=1
	  
output = json.dumps(results)
f = open(project_name+"_task_runs.json",'w')
f.write(output)
f.close()  


# now get the tasks -- note the exact same logic as the above loop
task_url = "http://crowd.globalfishingwatch.org/api/task?project_id="+str(project_id)+"&limit=100&offset="
page = 0
tasks = []
while 1:
	res = requests.get(task_url+str(page*100))
	if int(res.headers['X-RateLimit-Remaining']) < 10:
	    time.sleep(300) # Sleep for 5 minutes
	else:
		j = json.loads(res.text)
		if len(j)==0:
			break
		tasks = tasks + j		
		print "downloading " , task_url+str(page*100)
  		page +=1

output = json.dumps(tasks)
f = open(project_name+"_tasks.json",'w')
f.write(output)
f.close()  

