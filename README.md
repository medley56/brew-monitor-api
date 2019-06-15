# Fermentation Monitoring and Control
The brew monitor api is a Django app that uses beacontools and celery 
to record iBeacon data from a Tilt Hydrometer and insert that data into
a Django-backing database. We use Django REST Framework to 
provide a fully RESTful API that, for better or worse, fully 
support HATEOAS.

# Installation
## Installing beacontools
There's probably a way to automate this from requirements.txt but here is 
the step-by-step

0. Install libbluetooth headers and libpcap2:
`sudo apt-get install python-dev libbluetooth-dev libcap2-bin`
0. Grant the python executable permission to access raw socket data:
`sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python))`
0. Install beacontools with scanning support:
`pip install beacontools[scan]`

## Installing celery systemd service files
Copy the service files and their config to the correct locations.
```
cp deploy/celery /etc/conf.d/
cp deploy/celery.service /etc/systemd/system/
cp deploy/celerybeat.service /etc/systemd/system/
```
Ensure that the logging directories are setup at 
`/var/log/celery` and `/var/run/celery` and owned by the 
user specified in the `.service` files 
(this can be changed locally to fit your installation)

# Usage
Once everything is installed and the venv is properly set up,
run `python manage.py runserver`, followed by  `sudo systemctl start celery` and 
`sudo systemctl start celerybeat`. 
Go to [http://localhost:8000/brew-monitor/api/] to set up devices,
fermentations, datasets. To record data there must be a Tilt Device
in the DB associated with a fermentation.