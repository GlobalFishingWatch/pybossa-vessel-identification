import argparse
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json


# After running this code, you have to upload the files to gcloud
# !gsutil -m cp *  gs://gfw-crowd/lc/
# and then 
# gsutil -m acl set -R -a public-read gs://gfw-crowd/lc/


#ranges of the years
year_range = [2015]
month_range =[i for i in range(1,13)]

# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)

'''
# Query to create the subtable we are going to select from:
SELECT lat, lon, speed, mmsi, timestamp FROM TABLE_DATE_RANGE([pipeline_normalize.], TIMESTAMP('2015-01-01'), TIMESTAMP('2015-12-31')) 
where mmsi in (366596000,412470513,338060001,412422683,338167955,412286255,413812853,271072459,413249760,900006259,808464440,412413294,316020229,413814759,219001522,412420113,319089900,235033532,257007500,419020400,412449013,563242000,310413000,227588930,412436564,412331103,403710210,265581290,273443410,413359160,244153064,413952099,251809240,428381000,412464768,413817042,412427901,247190200,312763000,367135050,211567400,235054856,412332666,211460330,257990330,412413207,219001976,412413987,219002847,205521590,257898500,413007018,138005330,204243000,257888290,412402510,247081090,413854214,412349332,412854785,412436395,412417375,412443226,247082800,538005340,745003500,538003761,224083650,416059670,303221000,257866500,224123490,412331754,412460108,412462626,351239000,413787833,419064300,238984610,412326878,900019558,235097311,412451035,219345000,257151720,247030180,130700281,412125015,235114706,235004900,227308110,247149040,413781495,412284865,413952991,263406940,412329694,235102113,412464585,412435108,224952180,800038035,412417368,518348000,367584690,412436315,251518240,440002645,412434232,224102280,219002047,273352280,412201192,234423000,370418000,257575090,265631320,412321399,227058720,440117740,775911000,412353012,235032001,412301001,224173230,412428847,247149020,412449303,257108620,367045260,222222212,251402110,440103270,412001238,244250329,265658020,247142090,211484000,244615605,224018520,367681050,227808000,251792540,200005911,228008900,235076295,710289219,710000975,413775608,412416543)
and lat is not null and lon is not null and timestamp is not null and speed is not null and lat<90 and lat>-90 and lon<180 and lon>-180 and lon !=0 and lat !=0
'''


vessels = [366596000,412470513,338060001,412422683,338167955,412286255,413812853,271072459,413249760,900006259,808464440,412413294,316020229,413814759,219001522,412420113,319089900,235033532,257007500,419020400,412449013,563242000,310413000,227588930,412436564,412331103,403710210,265581290,273443410,413359160,244153064,413952099,251809240,428381000,412464768,413817042,412427901,247190200,312763000,367135050,211567400,235054856,412332666,211460330,257990330,412413207,219001976,412413987,219002847,205521590,257898500,413007018,138005330,204243000,257888290,412402510,247081090,413854214,412349332,412854785,412436395,412417375,412443226,247082800,538005340,745003500,538003761,224083650,416059670,303221000,257866500,224123490,412331754,412460108,412462626,351239000,413787833,419064300,238984610,412326878,900019558,235097311,412451035,219345000,257151720,247030180,130700281,412125015,235114706,235004900,227308110,247149040,413781495,412284865,413952991,263406940,412329694,235102113,412464585,412435108,224952180,800038035,412417368,518348000,367584690,412436315,251518240,440002645,412434232,224102280,219002047,273352280,412201192,234423000,370418000,257575090,265631320,412321399,227058720,440117740,775911000,412353012,235032001,412301001,224173230,412428847,247149020,412449303,257108620,367045260,222222212,251402110,440103270,412001238,244250329,265658020,247142090,211484000,244615605,224018520,367681050,227808000,251792540,200005911,228008900,235076295,710289219,710000975,413775608,412416543]

for mmsi in vessels:
    print mmsi
    try:
        query_request = bigquery_service.jobs()
        query_data = {
            'query': (
                '''SELECT
                      lat,
                      lon,
                      timestamp,
                      speed
                    FROM
                      [scratch_david_vesselsPyBossa.vessels_20160310_lc]
                    WHERE
                      mmsi ='''+str(mmsi)+'''
                    ORDER BY
                      timestamp ;''')
        }

        query_response = query_request.query(
            projectId='world-fishing-827',
            body=query_data).execute()

        sogs =[]
        timestamps = []
        lats = []
        lons = []
        
        print('Query Results:')
        if 'rows' in query_response:
            for row in query_response['rows']:
                #print row['f'][0]['v']
                lat = round(float(row['f'][0]['v']),5)
                lon = round(float(row['f'][1]['v']),5)
                sog = round(float(row['f'][3]['v']),1)
                t = int(float(row['f'][2]['v']))
                timestamp = datetime.utcfromtimestamp(t)
                sogs.append(sog)
                lats.append(lat)
                lons.append(lon)
                timestamps.append(timestamp)
                #print('\t'.join(field['v'] for field in row['f']))

    except HttpError as err:
        print('Error: {}'.format(err.content))
        raise err

    for y in year_range:
        for m in month_range:
            m_lats = []
            m_lons = []
            m_sogs = []
            m_timestamps = []
            for i in range(len(lats)):
                if timestamps[i].month == m and timestamps[i].year == y:
                    m_lats.append(lats[i])
                    m_lons.append(lons[i])
                    m_timestamps.append(str(timestamps[i]))
                    m_sogs.append(sogs[i])

            if len(m_lats)>100: #has to have at least 100 positions in the month
                js = {}
                js['lats']=m_lats
                js['lons']=m_lons
                js['sogs']=m_sogs
                js['timestamps']=m_timestamps
                # js['type'] = "LineString"
                # js['coordinates'] = [[round(lon,5),round(lat,5)] for lat,lon in zip(lats,lons)] #stupid to have higher than 5 digets
                t = json.dumps(js)
                f = open("../../data/vessels_20160310_lc/"+str(mmsi)+"_"+str(y)+"_"+str(m)+".json",'w')
                f.write(t)
                f.close()
            else:
                print "month: ",m," no values for "+str(mmsi) 

