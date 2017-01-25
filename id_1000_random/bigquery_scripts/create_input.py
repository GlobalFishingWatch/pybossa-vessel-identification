from os import listdir
from os.path import isfile, join
import random
from operator import itemgetter


mypath = "../../data/vessels_20160609/"
files = [f.replace(".json","") for f in listdir(mypath) if isfile(join(mypath, f)) and ".json" in f]

vessels_doubled = [f.split("_")[0] for f in files]
vessels = []
for v in vessels_doubled:
	if v not in vessels:
		vessels.append(v)




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

        #2014, then 2015
        print str(v)+"\t"+",".join(selects2)+"\t"+ (",".join(selects))
        # print (",".join(selects2))
        # two_files = random.sample(set(selects), 2)
        # for t in two_files:
        #     t = t.split("_")
        #     print t[0]+"\t"+t[1]+"\t"+t[2].split(".")[0]
    

