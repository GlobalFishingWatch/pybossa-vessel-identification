
import csv
import json
import urllib2
import matplotlib.pyplot as plt
import time

sourcedir = ''
filename = 'tasks_months.csv'


def make_histogram(mmsi, months_2014, months_2015):

    sogs = []
    for m in months_2014:
        if m!= "":
            url = 'http://storage.googleapis.com/gfw-crowd/'+mmsi+"_2014_"+m+".json"
            print url
            try:
                f = urllib2.urlopen(url)
                myfile = f.read()
                j = json.loads(myfile)
                sogs += j['sogs']
            except:
                time.sleep(5)
                try:
                    f = urllib2.urlopen(url)
                    myfile = f.read()
                    j = json.loads(myfile)
                    sogs += j['sogs']
                except: 
                    print "no file for ", url
    for m in months_2015:
        if m != "":
            url = 'http://storage.googleapis.com/gfw-crowd/'+mmsi+"_2015_"+m+".json"
            print url
            try:
                f = urllib2.urlopen(url)
                myfile = f.read()
                j = json.loads(myfile)
                sogs += j['sogs']
            except:
                time.sleep(5)
                try:
                    f = urllib2.urlopen(url)
                    myfile = f.read()
                    j = json.loads(myfile)
                    sogs += j['sogs']
                except: 
                    print "no file for ", url
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
     
        # Prints: [8.0, 6.0]         
        # Set figure width to 12 and height to 9
        fig_size[0] = 9
        fig_size[1] = 2.5
        plt.rcParams["figure.figsize"] = fig_size    
        plt.gcf().subplots_adjust(bottom=0.20)

        fig.set_size_inches(fig_size[0] , fig_size[1] )
        fig.savefig("vessels/"+str(mmsi)+'.png', dpi=100, bbox_inches='tight')
        print "succeed, ", mmsi
        plt.clf()
    else:
        print "not enough data for ",mmsi

    # plt.show()



with open(sourcedir + filename,'rU') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        mmsi = row['mmsi']
        months_2014 = row['months_2014'].split(",")
        months_2015 = row['months_2015'].split(",")
        make_histogram(mmsi, months_2014, months_2015)




