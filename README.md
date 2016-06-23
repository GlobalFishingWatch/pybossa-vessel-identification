# Pybossa Vessel Identifcation

The goal of this project is to categorize vessels and fishing behavior based on their tracks and information from the web. 

To see how to install PyBossa, see installation.md

Each file in this repo corresonds to a different project in PyBossa, except `results`, which is where results are stored, and `stylesheets`, where the css files for the projects are stored (most projects share css files -- these css files are uploaded to google cloud storage). 


### Input Files for the PyBossa Projects
All of the projects load the tracks of a given vessel for a given month from a json file that is stored in google cloud storage. Most are stored in the folder `http://storage.googleapis.com/gfw-crowd/`, although some are in variants of this. Most vessels also have an image of a histogram associated with it, which is usally stored in `http://storage.googleapis.com/gfw-crowd/histogram/`. 

All the json files have the following format:

```
{'sogs':[list of speeds, in knots, rounded to a tenth of a degree],
'timestamps':[list of timestamps, stored as strings],
'lats':[list of latitudes],
'lons':[list of longitudes]}
```

And all files have the format `{mmsi number}_{year}_{month}.json`. So mmsi 123456789 on January of 2015 would be `123456789_2015_1.json`
The histograms are for the entire preiod of data, and are just the mssi number. so for vessel 123456789, it would be `123456789.png`

### Template and html files

In each of the projects are the follow files for these projects:

* **project.json**: a JSON file that describes the project.
* **long_description.md**: a Markdown file with a long description of the
  project.
* **template.html**: the task presenter where the user/volunteer will identify vessel tracks
* **tutorial.html**: a simple tutorial that explains how to identify vessels

The file `template.html` is where all of the javascript goes, and which houses most of the infrastructure for the project. The other files require only light editing. It is critical to give the project a unique name and id in the file `project.json`, and to make sure this id is used throughout the above files. If you don't, `tutorial.html` and `template.html` will redirect you to a different project.

To create a project and upload these files, it is easiest to use the PyBossa command-line tool. Start by installing it:
```bash
    $ pip install pybossa-pbs
```
To create the project, while in the project directory, run:
```bash
    $ pbs --server <<url of the pybossa instance>> --api-key <<your api key>>  create_project
```

Whenver you want to push changes to the website, you ahve to run pbs update_project:
```bash
    $ pbs  --server <<url of the pybossa instance>> --api-key <<your api key>> update_project
```

Note that the stylesheets that I created have to be uploaded to Google Cloud Storage and made public. (I think you can put them on the PyBossa server instead, but it was easier to use GCS). Most projects use the css file `idtracks_pbossa.css`:

```bash
gsutil cp idtracks_pbossa.css  gs://gfw-crowd/task_assets/idtracks_pbossa.css
gsutil acl set public-read gs://gfw-crowd/task_assets/idtracks_pbossa.css
```
and this file is now available at http://storage.googleapis.com/gfw-crowd/task_assets/idtracks_pbossa.css  

Then you have to upload tasks

### Uploading Tasks
Tasks for each project are stored in a csv file. We can decide what the columns are, but we also need to make sure the template.html file is set up to accept these columns.

For most projects, the tasks file has the mmsi, year, and month (or a list of months) of the task, as well as sometimes a label such as the vessels geartype (e.g. "purse seiner"). The specifics for each project are listed below. Once the tasks are ready to upload, you can do so with this command:
```bash
    $ pbs  --server <<url of the pybossa instance>> --api-key <<your api key>> add_tasks --tasks-file <<task file name.csv>>
```
Note that it is a pain to delete tasks, so only do this once you really mean it.

### Current Projects
The projects are listed below by the the name of the folder they are in and then the name on Pybossa

##### maptests2 | Identifying Fishing Vessels
http://crowd.globalfishingwatch.org/project/maptests2/
This poorly named project is to identify different types of fishing vessels, and the input was random vessels from the likely fishing list.
The task file has three columns, `mmsi`, `months_2014`, and `months_2015`
`months_2014` and `months_2015` are populated by comma seperated strings, listing the months that are available for that given vessel. So, "1,2,3,4,8" means that that vessel has tracks for January, February, March, April, and August of that year

The results were originally stored a string, giving the classification identified by the user, but then later results were stored as a json obejct so that we could increase the number of fields. The fields in later results are:
`mmsi`, `vesselType` (the vessel type they identified), `search` (did they search for the vessel online) and `search_url` (relevant urls that include information about this vessel) 

We currently aren't adding more tasks to this project.

##### verify_message5and24 | Verify Vessel Identification
For this project, we obtained ~200 vessels for each of the vessel types as broadcast in the tpye 5 and 24 AIS messages. Basically, we were testing to see if the vessels were what they said they were. 
The task input for this is `mmsi`,`label`, where the label is what the vessel reported in the type 5 and 24 messages.

##### id_fishing_vessels_hclc | Reviewing Model Output, High Confidence, Low Label Confidence
This project was developed to test an early version of the neural net (early March 2016). We selected vessels that had a high confidence according to the Neural Net, but which identified themselves as something else in their type 5 and 24 messages. Dalhousie students worked on some of these tasks, and too many of them were difficult to identify so we stopped using this project.

##### id_fishing_vessels_lc | Reviewing Model Output, Low Confidence Fishing Vessels
This project was developed to test an early version of the neural net (early March 2016). We selected fishing vessels that had a low confidence as identified by the neural net, but which identified as fishing vessels in their type 5 and 24. This project was never used.

##### id_fishing_vessels_v2 | Identifying Fishing Vessels
This is an updated version of maptests2, and is where we have loaded various vessels to be identified.
194 vessels have been identified in this project, mostly by Dalhousie students.
The input is the same as maptests2, except that we didn't include any tracks from 2014, so the tasks file has columns only for `mmsi` and `months_2014`
The results are the same format at the later results from maptests2: `mmsi`, `vesselType` (the vessel type they identified), `search` (did they search for the vessel online) and `search_url` (relevant urls that include information about this vessel) 

##### id_river_vessels | Identifying River Vessels
For this project, we drew bounding boxes around the Mississippi, the Danube / Rhine, and the Amazon and selected a random set of boats that had at least 200 points in these bounding boxes. The idea was to classify river vessels.
The results are in the same format as id_fishing_vessels_v2

##### neural_net_test | Verify the Neural Net
This project was to test a very early version of the nerual net classifier -- I believe from January of 2016. Although 821 tasks were loaded, we never used this project. 

##### id_random_vessels | Identifying Random Vessels
This project is to identify a random set of mmsi to see how well our model is doing compared to an unbiased, random sample. 
The results are the same format as id_fishing_vessels_2

##### id_fishing_points | Identify Fishing Behavior
This project is used to classify individual points as fishing and non-fishing. Each task is a single month from a single vessel. The task file input csv has four fields: `mmsi`, `year`, `month`, and `vesselType`. `vesselType` is just used to display to the user what type of vessel they are classifying.

The results are stored as a json object with the following fields:
`mmsi`,`vesselType` (same as the input value -- the user doesn't select this), `text_notes` (a string that the user can enter), `confidence` (the users confidence in the results -- "no_confidence" means ignore these results), and `fishingArrayString` (a string of 1s, 0s, and 2s).
the `fishingArrayString` is the classification of each point. 0 is nonfishing, 1 is fishing, and 2 is not sure. 
To line up these results with the underlying data, you have to download the json file with the tracks in it. That json file is in the format `{mmsi number}_{year}_{month}.json`. So mmsi 123456789 on January of 2015 would be `123456789_2015_1.json`, stored at `http://storage.googleapis.com/gfw-crowd/+{json file name}`


### Creating Input Data for the Projects
To create the json files, the follow steps have to take place:
 - A lit of mmsi must be selected to be classified. The vessels selected depend on the project.
 - A table is created in BigQuery that has only the position of these mmsi.
 - This table is either queried for each mmsi, or it is downloaded as big csv file, and then a script loops throuh it and produces the json file for each mmsi for each month. Generally, if there are fewer than 100 points for a month, the scripts don't create a file.
 - These json files are uploaded to Google Cloud Storage and the permisisons are set to be publically readible
 - For a number of the projects, a histogram is also created, which is a histogram of the speeds of that vessel (excluding speeds slower than .1 knots) over all the json files for that vessel. 
 - A tasks csv file is created, and this file varies depending on the project.

For many of the above projects, there is a folder `bigquery_scripts` which has some of the scripts used to create the json files. The most efficient version is in the project `id_fishing_points`, which does all of these steps in a few python scripts, which can be found in the folder `creating_tasks` in this project. 


### Generating Results
The results of PyBossa can be obtained using their api. In the folder results, there is a Python script `download_results.py` that can be run from the command line as follows: `!python download_results.py {project_id}`. This will download all tasks and tasks_runs from a given project. Each will be a list of json objects. The harder task is then to interpret these tasks, and figure out what to do when different users disagree. 

Note that many of the projects have a folder `results` in them, where there are some python scripts that create csv files with the output of the project. These have all been produced in a one-off fashion, and it would be much better if there was some form of standardization.
