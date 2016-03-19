import argparse
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json


# After running this code, you have to upload the files to gcloud
# !gsutil -m cp *  gs://gfw-crowd/hclc/
# and then 
# gsutil -m acl set -R -a public-read gs://gfw-crowd/hclc/


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
where mmsi in (247119520,576190000,338139723,440105520,231006000,224006770,574013003,235095543,538002948,431900227,224724000,432568000,503652100,533065200,367588860,576690000,235000632,503013020,416028700,235090871,212121212,710472000,416731000,367161340,441735000,251199000,601032600,416046700,419000244,503586100,235096548,273847710,311227000,316017683,211465950,525022136,211154980,354055000,265722600,566174000,533130177,525023216,366920680,657429000,367571490,431601350,416004242,265638130,431501545,367599150,333300758,264160092,245999000,412570440,412702190,412426090,376761000,524801490,440127950,419072800,413963176,413814162,413787715,413977702,413976502,227241250,247191500,900116912,413964488,205687000,413900088,413792516,525015561,457239000,413553190,227015120,413807411,412428493,413814949,209128000,273315640,900008509,412888880,659422000,412429460,413984759,238198000,250414000,412798016,413999862,710012560,353494000,412421520,413002549,224770000,667001230,352432000,413987973,413553230,219133000,503553100,249000066,235091473,413779571,235106574,352689000,224084620,413808319,413782871,244790381,413811523,224503230,525005013,413762607,701319841,413809107,367666000,413982134,224935540,440103090,227258290,338173208,413830574,413802042,413766622,257779360,413950083,244650004,503571400,338175418,725003280,250000111,333888999,400121500,263906380,900899965,224012730,235002453,244780598,413996094,413962155,412434226,338145727,413767005,572718210,525022145,503008850,431004641,982358863,224226870)
and lat is not null and lon is not null and timestamp is not null and speed is not null and lat<90 and lat>-90 and lon<180 and lon>-180 and lon !=0 and lat !=0
'''


vessels = [247119520,576190000,338139723,440105520,231006000,224006770,574013003,235095543,538002948,431900227,224724000,432568000,503652100,533065200,367588860,576690000,235000632,503013020,416028700,235090871,212121212,710472000,416731000,367161340,441735000,251199000,601032600,416046700,419000244,503586100,235096548,273847710,311227000,316017683,211465950,525022136,211154980,354055000,265722600,566174000,533130177,525023216,366920680,657429000,367571490,431601350,416004242,265638130,431501545,367599150,333300758,264160092,245999000,412570440,412702190,412426090,376761000,524801490,440127950,419072800,413963176,413814162,413787715,413977702,413976502,227241250,247191500,900116912,413964488,205687000,413900088,413792516,525015561,457239000,413553190,227015120,413807411,412428493,413814949,209128000,273315640,900008509,412888880,659422000,412429460,413984759,238198000,250414000,412798016,413999862,710012560,353494000,412421520,413002549,224770000,667001230,352432000,413987973,413553230,219133000,503553100,249000066,235091473,413779571,235106574,352689000,224084620,413808319,413782871,244790381,413811523,224503230,525005013,413762607,701319841,413809107,367666000,413982134,224935540,440103090,227258290,338173208,413830574,413802042,413766622,257779360,413950083,244650004,503571400,338175418,725003280,250000111,333888999,400121500,263906380,900899965,224012730,235002453,244780598,413996094,413962155,412434226,338145727,413767005,572718210,525022145,503008850,431004641,982358863,224226870]


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
                      [scratch_david_vesselsPyBossa.vessels_20160310_hclc]
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
                f = open("../../data/vessels_20160310_hclc/"+str(mmsi)+"_"+str(y)+"_"+str(m)+".json",'w')
                f.write(t)
                f.close()
            else:
                print "month: ",m," no values for "+str(mmsi) 

