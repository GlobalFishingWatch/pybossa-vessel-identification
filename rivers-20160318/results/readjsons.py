#! /usr/bin/python
import urllib2
import json

task_ids = []

with open('id_river_vessels_task 5.json') as data_file:    
    data = json.load(data_file)
    for d in data:
        task_ids.append(d['id'])

print task_ids


link = 'http://crowd.globalfishingwatch.org/project/maptests2/409/results.json'


#users
users = ["" for i in range(21)]
users[1]='davidkroodsma'
users[3]='davidkroodsmathe2nd'
users[4]='alexwilson'
users[5]='chris'
users[2]='bjornbergman'
users[6]='enriquetuya'
users[7]='kristinaboerder'
users[8]='vaiduke2'
users[9]='katepepler'
users[10]='stephanielewis'
users[11]='AlexCerra'
users[12]='juliecharbonneau'
users[13]='ninagalle'
users[14]='sidneyblack-rotchin'
users[15]='daivdtest'
users[16]='cailinburmaster'
users[17]='elizabethnagel'
users[18]='isabelfleisher'
users[19]='ciarawillis'
users[20]='clairechristie'

user_count = [0 for i in range (21)]

# download tasks
# for t in task_ids:
#     response = urllib2.urlopen('http://crowd.globalfishingwatch.org/api/taskrun?task_id='+str(t))
#     html = response.read()
#     f = open("jsons/"+str(t)+".json", 'w')
#     f.write(html)
#     f.close()

outfile = open('results.txt', 'w')
outfile.write('mmsi\tlink\tusers\tresponses\tlongliner\tpursseiner\ttrawler\treefers\tmultigear\tother fishing\tnotfishing\tmultiple\tbaddata\tnot known\tother\tothertext\twebsitesfound\n')

for t in task_ids:
    f = open("jsons/"+str(t)+".json",'rU')
    contents = f.read()
    f.close()
    j = json.loads(contents) 
    if len(j):
        v = json.loads(j[0]['info'])
        print v['mmsi'],v['vesselType']

#     longliner = 0
#     pursseiner = 0
#     trawler = 0
#     reefer = 0
#     multigear = 0
#     otherfish = 0
#     notfishing = 0
#     multiple = 0
#     baddata = 0
#     other = 0
#     othertext = ''
#     dunno = 0
#     findyes = 0
#     findno = 0
#     didntsearch = 0
#     websitesfound = ''
#     theusers = ''
#     previous_version_response = 0

#     contents = f.read()
#     f.close()
#     j = json.loads(contents)
#     responses = 0
#     for k in j:
#         if len(k['info'])<20:
#             previous_version_response += 1
#         elif k['user_id'] != 1: #ignore david's results
#             responses += 1
#             r = json.loads(k['info'].replace("\n",""))
#             vt = r['vesselType']
#             if vt.lower() == 'trawler': trawler += 1
#             elif vt == 'purse_seine': pursseiner += 1
#             elif vt == 'longliner': longliner += 1
#             elif vt == 'reefer': reefer += 1
#             elif vt == 'muti_gear': multigear += 1
#             elif vt == 'other fishing ' or vt == "other_fishing" or vt == "other fishing" or vt == " other fishing": otherfish += 1
#             elif vt == 'not_fishing': notfishing += 1
#             elif vt == 'multiple_vessles': multiple += 1
#             elif vt == 'bad_data' or vt == 'not_enough_data': baddata += 1    
#             elif vt == 'not_known': dunno += 1
#             else:
#                 othertext += vt+","
#                 other += 1
#                 #print vt
#             if r['search_url']: websitesfound += r['search_url']+","
#             #print k['user_id']
#             theusers += users[k['user_id']] + ","
#             user_count[k['user_id']]+=1
 
#     link = "http://crowd.globalfishingwatch.org/project/maptests2/task/"+str(j[0]['task_id'])
#     websitesfound = websitesfound[:-1] # get rid of comma at the end
#     theusers = theusers[:-1] #get rid of comma at the end
#     if len(othertext)>1: othertext = othertext[:-1] #get rid of comma at the end
#     thetext = r['mmsi']+"\t"+link+"\t"+theusers+"\t"+str(responses)+"\t"+str(longliner)+"\t"+str(pursseiner)+"\t"+str(trawler)+"\t"+ \
#          str(reefer)+"\t"+str(multigear)+"\t"+str(otherfish)+"\t"+str(notfishing)+"\t"+str(multiple)+"\t"+ \
#              str(baddata)+"\t"+str(dunno)+"\t"+str(other)+"\t"+othertext+"\t"+websitesfound
#     outfile.write(thetext.replace("\t0","\t")+ "\n")

# for i in range(len(user_count)):
# 	if user_count[i]:
# 		print users[i],"\t",user_count[i]

outfile.close()

            # print r['search_url'], r['mmsi'], r['vesselType'], r['search']
#            u'search_url': u'', u'mmsi': u'412002777', u'vesselType': u'longliner', u'search': u'Yes'
            # exit()



#js = json.loads(html)
#for j in js:
    
