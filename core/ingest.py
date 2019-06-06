"""
Classes and functions for ingesting data into the sqlite DB from the iBeacon messages of the Tilt Hydrometer
"""

import sqlite3
import datetime as dt
from beacontools import BeaconScanner

def callback(bt_addr, rssi, packet, additional_info):
    print(type(additional_info))
    if not (900 < additional_info['major'] < 1150):
        return
    if not (0 < additional_info['minor'] < 212):
        return
    temp = additional_info['minor']
    sg = additional_info['major']
    time = dt.now()

    print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))

def search_for_devices(): 
    scanner = BeaconScanner(callback)
    scanner.start()
