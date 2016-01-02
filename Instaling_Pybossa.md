#Installing Pybossa

The following outlines how to install PyBossa on Google Cloud virtual machine.

This is how I set up PyBossa. I followed the instructions from [on installing PyBossa by hand](http://docs.pybossa.com/en/latest/install.html), and made two small modifications:
* We didn't clone the master -- instead we got the most recent release. Which was v1.3.0
* I needed to install one more python library that was not included in requirements. I note it below (pip install Flask-Misaka). It would probably be good to know why I had to do this, as I should not have had to given the instructions.

Anyway, here it goes:

###1 Create and configure Google Cloud Virtual Machine
Settings:
* Ubuntu 4.04
* Allow http and https traffic, and api access (although these may not matter)
* add the tag “pybossa-dev” -- this allows us to access the port 5000. Eventually we need to set up real server to allow access to this instance of PyBossa.

###2 SSH into the Virtual Machine

and do the following:
```bash
sudo apt-get update
sudo apt-get install python-pip
sudo apt-get install git-core
sudo apt-get install postgresql postgresql-server-dev-all libpq-dev python-psycopg2
sudo apt-get install python-virtualenv
sudo apt-get install python-dev build-essential libjpeg-dev libssl-dev swig libffi-dev
git clone --recursive --branch v1.3.0 https://github.com/PyBossa/pybossa
cd pybossa
virtualenv env
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
cp settings_local.py.tmpl settings_local.py
cp alembic.ini.template alembic.ini
sudo apt-get install redis-server
redis-server contrib/sentinel.conf --sentinel
sudo su postgres
createuser -d -P pybossa
```
when promted, enter "tester" as the password.
```bash
createdb pybossa -O pybossa
exit
```
**HERE'S THE STEP I HAD TO ADD.** the next parts weren't working. I looked at the error message, and it looked like some libraries weren't working quite right. I found that if I installed Flask-Miaka, like the following, it then worked. I don't know why. 
```bash
pip install Flask-Misaka 
```
Now the following two commands with get everything running. I ran "nohup" so that I could disconnect and have PyBossa still running. See [Deploying PyBossa with nginx and uwsgi](http://docs.pybossa.com/en/latest/nginx.html#deploying-pybossa-with-nginx-and-uwsgi) for how to really set up the server.
```bash
python cli.py db_create
nohup python run.py &
```
