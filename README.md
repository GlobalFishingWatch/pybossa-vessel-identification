# Pybossa Vessel Identifcation

The goal of this project is to categorize vessels based on their tracks and information from Marine Traffic. This was originally made by modifying the [PyBossa FlickrPerson Example App] (https://github.com/PyBossa/app-flickrperson)

To see how to install PyBossa, see installation.md

There are currently two different crowdsourcing projects in this RePo, in the folders VerifyVessels and FishingVesselID.

VerifyVessels is used to check to see if the neural net correctly identified vessels.
FishingVesselID is used to identify different types of vessels.


In each of these folders are the follow files for these projects:

* **project.json**: a JSON file that describes the project.
* **long_description.md**: a Markdown file with a long description of the
  project.
* **template.html**: the task presenter where the user/volunteer will identify vessel tracks
* **tutorial.html**: a simple tutorial that explains how to identify vessels
* **idtracks_pbossa.css**: css for the the template (mostly helps the layout of the d3 charts)

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

These _have_ to correspond to a file stored in google cloud. 
To add the tasks, type, while in this directory: 

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
