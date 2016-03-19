import argparse
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from datetime import datetime
import json



# After running this code, you have to upload the files to gcloud
# !gsutil -m cp *  gs://gfw-crowd/river/
# and then 
# gsutil -m acl set -R -a public-read gs://gfw-crowd/river/


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
where mmsi in (267010021,366967640,269057408,367505770,477581600,203999327,413961936,412455390,267168000,366996080,366851250,244660073,345010030,211087743,413779267,367682130,366937040,413766165,244660360,413790909,413979753,413829474,413777098,413521140,413784139,211514140,413893000,413801945,413824096,413823514,808664168,514814000,370170000,366984180,367057370,413831093,413996682,413823601,413790301,413813096,413961301,211512760,413453680,413952938,413806175,413951241,413823918,413819373,413978287,270256000,413778785,413771406,413779089,413794658,413805206,413826012,412553970,413552560,413811461,413953900,413793224,413827421,413803337,413974073,412418190,261186310,413804286,413780051,413827566,412733000,412425010,413792801,312762000,413802174,413826623,413795331,413981938,413973986,413794382,413973417,413770331,372879000,413785998,244660717,413787875,413772055,413812908,413961902,413794909,413818027,413811254,413778851,413760448,413775835,413801647,413953113,244650869,413780352,413077030,413808025,413792522,413777355,413819438,413777417,413812652,441906000,413784964,413760814,413972528,413782376,412357040,413819608,413976243,412502540,413787476,413963568,413783618,413794405,413809739,413808953,413791278,413819096,413855917,413813082,413940365,413615000,211553330,413963997,413791479,413957835,413773228,413964973,413971066,413774853,413964127,413780618,413952638,413815205,413827288,413783337,413794467,413964392,413827735,413973889,413822424,413823538,413768848,413355150,413978527,413821431,413972173,413987031,413850163,413803586,413954433,413819656,413855827,413989907,413965748,413773731,413762495,413812753,413760869,413817683,413980123,412375550,413806165,413772083,413825000,413416390,413829726,413794812,413827195,413973583,412439570,413964028,367611460,413508160,413828525,413353940,413858942,413810047,413821235,413808125,413807196,413801402,413827446,514210000,413816815,413828665,413812924,514438000,413782444,413771745,413829708,371592000,413994615,413817042,413965376,413956467,413787406,413964816,413789105,413787071,413812741,413974748,413821081,413353890,413806878,412502550,413811037,413812138,413986394,413806304,413975862,413783723,413996359,413800616,147258369,227734020,413810013,413811435,413979316,413789725,413784282,566507000,413810716,413780786,413963998,413964935,229623000,244660065,413779775,412112015,371758000,413790959,413507110,413779598,413994693,413794528,538005160,370963000,477434100,413996245,413760471,413807561,413978119,413778444,244670275,413785293,413783957,413700074,413982097,413766754,249058000,413773159,477685900,414093000,413454260,373674000,413956891,413988537,413769838,413980855,900004474,533930000,405000135,412501180,413800049,600008305,413442070,244650959,413764977,413470530,356503000,235654664,412552940,477685200,211514790,538005085,244700114,356779000,412429060,477924000,371558000,366985540,367513420,249300300,203999358,211660140,412760780,366916920,413773674,413984799,367638240,211196560,366985050,211269090,211644170,366991790)
and lat is not null and lon is not null and timestamp is not null and speed is not null and lat<90 and lat>-90 and lon<180 and lon>-180 and lon !=0 and lat !=0
'''
vessels = [267010021,366967640,269057408,367505770,477581600,203999327,413961936,412455390,267168000,366996080,366851250,244660073,345010030,211087743,413779267,367682130,366937040,413766165,244660360,413790909,413979753,413829474,413777098,413521140,413784139,211514140,413893000,413801945,413824096,413823514,808664168,514814000,370170000,366984180,367057370,413831093,413996682,413823601,413790301,413813096,413961301,211512760,413453680,413952938,413806175,413951241,413823918,413819373,413978287,270256000,413778785,413771406,413779089,413794658,413805206,413826012,412553970,413552560,413811461,413953900,413793224,413827421,413803337,413974073,412418190,261186310,413804286,413780051,413827566,412733000,412425010,413792801,312762000,413802174,413826623,413795331,413981938,413973986,413794382,413973417,413770331,372879000,413785998,244660717,413787875,413772055,413812908,413961902,413794909,413818027,413811254,413778851,413760448,413775835,413801647,413953113,244650869,413780352,413077030,413808025,413792522,413777355,413819438,413777417,413812652,441906000,413784964,413760814,413972528,413782376,412357040,413819608,413976243,412502540,413787476,413963568,413783618,413794405,413809739,413808953,413791278,413819096,413855917,413813082,413940365,413615000,211553330,413963997,413791479,413957835,413773228,413964973,413971066,413774853,413964127,413780618,413952638,413815205,413827288,413783337,413794467,413964392,413827735,413973889,413822424,413823538,413768848,413355150,413978527,413821431,413972173,413987031,413850163,413803586,413954433,413819656,413855827,413989907,413965748,413773731,413762495,413812753,413760869,413817683,413980123,412375550,413806165,413772083,413825000,413416390,413829726,413794812,413827195,413973583,412439570,413964028,367611460,413508160,413828525,413353940,413858942,413810047,413821235,413808125,413807196,413801402,413827446,514210000,413816815,413828665,413812924,514438000,413782444,413771745,413829708,371592000,413994615,413817042,413965376,413956467,413787406,413964816,413789105,413787071,413812741,413974748,413821081,413353890,413806878,412502550,413811037,413812138,413986394,413806304,413975862,413783723,413996359,413800616,147258369,227734020,413810013,413811435,413979316,413789725,413784282,566507000,413810716,413780786,413963998,413964935,229623000,244660065,413779775,412112015,371758000,413790959,413507110,413779598,413994693,413794528,538005160,370963000,477434100,413996245,413760471,413807561,413978119,413778444,244670275,413785293,413783957,413700074,413982097,413766754,249058000,413773159,477685900,414093000,413454260,373674000,413956891,413988537,413769838,413980855,900004474,533930000,405000135,412501180,413800049,600008305,413442070,244650959,413764977,413470530,356503000,235654664,412552940,477685200,211514790,538005085,244700114,356779000,412429060,477924000,371558000,366985540,367513420,249300300,203999358,211660140,412760780,366916920,413773674,413984799,367638240,211196560,366985050,211269090,211644170,366991790]


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
                       [scratch_david_vesselsPyBossa.vessels_20160318]
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
                f = open("../../data/vessels_20160318/"+str(mmsi)+"_"+str(y)+"_"+str(m)+".json",'w')
                f.write(t)
                f.close()
            else:
                print "month: ",m," no values for "+str(mmsi) 
