import argparse
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json
import os


'''
The mmsi for this are the first 300 from the file sent to me by Tim
'''

# After running this code, you have to upload the files to gcloud
# gsutil -m cp *  gs://gfw-crowd/
# and then 
# gsutil -m acl set -R -a public-read gs://gfw-crowd/


# set outdirector for the data, and then output to it
out_dir = '../../data/vessels_20160609/'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)


#ranges of the years
year_range = [2015]
month_range =[i for i in range(1,13)]

# Grab the application's default credentials from the environment.
credentials = GoogleCredentials.get_application_default()
# Construct the service object for interacting with the BigQuery API.
bigquery_service = build('bigquery', 'v2', credentials=credentials)

'''
# Query to create the subtable we are going to select from:
SELECT
  lat,
  lon,
  speed,
  mmsi,
  timestamp
FROM
  TABLE_DATE_RANGE([pipeline_normalize.], TIMESTAMP('2015-01-01'), TIMESTAMP('2015-12-31'))
WHERE
  mmsi IN (271040680,235093608,258849000,413769099,316012247,367424360,440707390,413810157,413780451,412206095,477257800,413786661,412437777,316026195,211123610,238794240,622122402,413769342,351896000,403702310,413021007,367702330,367578770,413825466,565736000,412214558,247101610,244730085,413794882,413412620,367178530,271002480,413994918,312044000,413900085,416458613,228317000,273378130,900003051,515321000,372815000,636090655,209250000,413275972,224196000,211538610,445184000,244132000,412450765,257188000,338386000,403117000,422041200,247223780,255805684,256221000,373014000,211219330,238603140,413455660,714430001,215450000,247056700,244690647,671638000,209272000,440154490,244770433,412330291,262018700,91602,477144400,357467000,477767600,232003427,900030051,413812104,351682000,245726000,510851668,413789241,408327000,205203890,416004693,353399000,309275000,244615515,10000000,338175418,431680066,412470385,273343610,412325462,574100006,345123650,413902945,503000050,316026269,412451798,235053796,412438123,366903030,503457800,271072875,412281451,538004788,247229700,440120270,211191060,412450642,413763442,227790860,279854123,244780400,271010036,412210804,413902616,247238900,205432790,244155000,755070000,311040800,367625820,440100890,477477100,413699920,413828158,211481333,211455520,413806106,441782000,413768942,207829830,338181123,419000149,416039500,412258000,378158000,219017917,368247000,503408000,413468210,710005981,412331957,111666888,412422173,235000322,413815211,244700601,211669240,413352290,229199000,374446000,352278000,636011247,538004593,440133360,319068200,345070404,314187000,210493000,413824535,244740130,367049000,412349395,205484990,271040865,412460206,247353600,413355540,412354920,259674000,457688000,413807511,367595180,351612000,413405390,351684000,227180930,477454600,441192000,235004244,413824757,230125940,477413400,229368000,251833940,413821764,352793000,2323112,244650956,247323200,414759000,423191100,229037000,271002039,224330760,419095500,211210910,205224490,367545060,419000883,235101302,423357100,219324000,416000487,234180000,412431147,244660655,412422926,237005100,540010800,413760167,241375000,235102119,412416298,413762174,477242400,413772262,566885000,440322840,247051770,235095796,503538700,900032011,413789424,211626470,432525000,255805540,412423257,413801486,247140370,244750489,770576229,553111710,412055008,227789190,244770751,269057320,567214369,432996000,412205651,413767114,355229000,273424120,413906419,249472000,403289000,41202506,271000278,412284636,565017000,413203840,413948000,413818555,273326070,710008410,235052172,367532830,211453140,413825093,205278690,259244000,413819268,413053560,230654000,563529000,211223790,477726600,667003235,375226000,563000450,440216160,235062382,412474090,412438724,510180000,245078000,725001123,247250150,367111870,366748260,244700955,371993000,412333029,636091349,412439407,366840330,244790786,413902547,413286900,227317660,413827536,265644320,273320100,271002141,414001075,240971000,235021371,271044221)
  AND lat IS NOT NULL
  AND lon IS NOT NULL
  AND timestamp IS NOT NULL
  AND speed IS NOT NULL
  AND lat<90
  AND lat>-90
  AND lon<180
  AND lon>-180
  AND lon !=0
  AND lat !=0'''
vessels = [271040680,235093608,258849000,413769099,316012247,367424360,440707390,413810157,413780451,412206095,477257800,413786661,412437777,316026195,211123610,238794240,622122402,413769342,351896000,403702310,413021007,367702330,367578770,413825466,565736000,412214558,247101610,244730085,413794882,413412620,367178530,271002480,413994918,312044000,413900085,416458613,228317000,273378130,900003051,515321000,372815000,636090655,209250000,413275972,224196000,211538610,445184000,244132000,412450765,257188000,338386000,403117000,422041200,247223780,255805684,256221000,373014000,211219330,238603140,413455660,714430001,215450000,247056700,244690647,671638000,209272000,440154490,244770433,412330291,262018700,91602,477144400,357467000,477767600,232003427,900030051,413812104,351682000,245726000,510851668,413789241,408327000,205203890,416004693,353399000,309275000,244615515,10000000,338175418,431680066,412470385,273343610,412325462,574100006,345123650,413902945,503000050,316026269,412451798,235053796,412438123,366903030,503457800,271072875,412281451,538004788,247229700,440120270,211191060,412450642,413763442,227790860,279854123,244780400,271010036,412210804,413902616,247238900,205432790,244155000,755070000,311040800,367625820,440100890,477477100,413699920,413828158,211481333,211455520,413806106,441782000,413768942,207829830,338181123,419000149,416039500,412258000,378158000,219017917,368247000,503408000,413468210,710005981,412331957,111666888,412422173,235000322,413815211,244700601,211669240,413352290,229199000,374446000,352278000,636011247,538004593,440133360,319068200,345070404,314187000,210493000,413824535,244740130,367049000,412349395,205484990,271040865,412460206,247353600,413355540,412354920,259674000,457688000,413807511,367595180,351612000,413405390,351684000,227180930,477454600,441192000,235004244,413824757,230125940,477413400,229368000,251833940,413821764,352793000,2323112,244650956,247323200,414759000,423191100,229037000,271002039,224330760,419095500,211210910,205224490,367545060,419000883,235101302,423357100,219324000,416000487,234180000,412431147,244660655,412422926,237005100,540010800,413760167,241375000,235102119,412416298,413762174,477242400,413772262,566885000,440322840,247051770,235095796,503538700,900032011,413789424,211626470,432525000,255805540,412423257,413801486,247140370,244750489,770576229,553111710,412055008,227789190,244770751,269057320,567214369,432996000,412205651,413767114,355229000,273424120,413906419,249472000,403289000,41202506,271000278,412284636,565017000,413203840,413948000,413818555,273326070,710008410,235052172,367532830,211453140,413825093,205278690,259244000,413819268,413053560,230654000,563529000,211223790,477726600,667003235,375226000,563000450,440216160,235062382,412474090,412438724,510180000,245078000,725001123,247250150,367111870,366748260,244700955,371993000,412333029,636091349,412439407,366840330,244790786,413902547,413286900,227317660,413827536,265644320,273320100,271002141,414001075,240971000,235021371,271044221]



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
                       [scratch_david_vesselsPyBossa.vessels_20160609]
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
                f = open(out_dir+str(mmsi)+"_"+str(y)+"_"+str(m)+".json",'w')
                f.write(t)
                f.close()
            else:
                print "month: ",m," no values for "+str(mmsi) 

