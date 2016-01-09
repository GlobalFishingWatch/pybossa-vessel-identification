#Installing Pybossa

The following outlines how to install PyBossa on Google Cloud virtual machine.

This is how I set up PyBossa. I followed the instructions from [on installing PyBossa by hand](http://docs.pybossa.com/en/latest/install.html), and made two small modifications:
* We didn't clone the master -- instead we got the most recent release. Which was v1.3.0
* I needed to install one more python library that was not included in requirements. I note it below (pip install Flask-Misaka). It would probably be good to know why I had to do this, as I should not have had to given the instructions.

Anyway, here it goes:

###1 Create and configure Google Cloud Virtual Machine
Settings:
* Ubuntu 14.04
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

## Nginx Proxy (Optional)

In order to have requests on port 80 there are two possibilities:
- Chaning the port on settings_local.py to 80. But this requires all steps on the setup to be done with sudo so it pybossa has rights for using port 80.
- Using a proxy.

Following steps are for setting up nginx on the GCE to attend the request on port 80.

1- Install nginx
```
sudo apt-get update
sudp apt-get install nginx
```
2- Add proxy configuration
```
sudo vim /etc/nginx/conf.d/proxy.conf
```
And enter the following configuration
```
server {

    listen 80;

    location / {

      proxy_set_header        Host $host;
      proxy_set_header        X-Real-IP $remote_addr;
      proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header        X-Forwarded-Proto $scheme;

      # Fix the "It appears that your reverse proxy set up is broken" error.
      proxy_pass          http://0.0.0.0:5000;
      proxy_read_timeout  90;
    }
  }
```
3- Remove default nginx page configuration:
```
sudo rm /etc/nginx/sites-available/default
sudo rm /etc/nginx/sites-enabled/default
```
4- Restart nginx service
```
sudo service nginx restart
```
# Restarting services

- Pybossa
```
cd PYBOSSA_DIR
virtualenv env
source env/bin/activate
nohup python run.py &
```
- Nginx
```
sudo service nginx restart|start|stop
```
