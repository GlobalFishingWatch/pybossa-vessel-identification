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

Then you have to upload tasks

### Uploading Tasks
Tasks for each project are stored in a csv file. We can decide what the columns are, but we also need to make sure the template.html file is set up to accept these columns.

For most projects, the tasks file has the mmsi, year, and month (or a list of months) of the task, as well as sometimes a label such as the vessels geartype (e.g. "purse seiner"). The specifics for each project are listed below. Once the tasks are ready to upload, you can do so with this command:
```bash
    $ pbs  --server <<url of the pybossa instance>> --api-key <<your api key>> add_tasks --tasks-file <<task file name.csv>>
```
Note that it is a pain to delete tasks, so only do this once you really mean it.

### Current Projects
The projects are listed below by their 

##### maptests2
This poorly named project is to identify 

#####

#####

#####

#####

#####

#####


### Creating Imp

There are currently two different crowdsourcing projects in this RePo, in the folders VerifyVessels and FishingVesselID.

VerifyVessels is used to check to see if the neural net correctly identified vessels.
FishingVesselID is used to identify different types of vessels.




# Updating the project
All of the files above, except idtracks_pbossa.css can be updated using pybossa-pbs

```bash
    $ pip install pybossa-pbs
```

To create the project, enter, while in this directory:

```bash
    $ pbs --server <<url of the pybossa instance>> --api-key <<your api key>>  create_project
```
The information about the task has to be in the project.json file

Then you can upload some tasks. These are in the format of a csv file, and they have to have a column for:
* mmsi
* month (1-12)
* year

These _have_ to correspond to a file stored in google cloud, stored in the bucket gfw-crowd
To add the tasks, type, while in the directory of one of these two projects type: 

```bash
    $ pbs  --server <<url of the pybossa instance>> --api-key <<your api key>> add_tasks --tasks-file <<task file name.csv>>
```
then
```bash
    $ pbs  --server <<url of the pybossa instance>> --api-key <<your api key>> update_project
```

Because I didn’t know where to put a stylesheet on the pybossa server, I uploaded it to google cloud and made it public there:

```bash
gsutil cp idtracks_pbossa.css  gs://gfw-crowd/task_assets/idtracks_pbossa.css
gsutil acl set public-read gs://gfw-crowd/task_assets/idtracks_pbossa.css
```
Now it is available and public at http://storage.googleapis.com/gfw-crowd/task_assets/idtracks_pbossa.css  
