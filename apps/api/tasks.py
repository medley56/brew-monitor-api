import pytz
import datetime as dt
import logging

from beacontools import IBeaconFilter, BeaconScanner
from apps.api.models import Datapoint, Dataset, Device, Fermentation
from celery import task


class TiltHydrometerLogger(object):
    """
    Manages logging and data insertion for tilt hydrometer
    """

    def __init__(self):
        ble_devices = Device.objects.filter(type='BLE')
        if len(ble_devices) == 0:
            raise ValueError('No bluetooth devices found in database.')
        self.uuids = [device.uuid for device in ble_devices]
        self.data = { uuid: {'T': [], 'SG': []} for uuid in self.uuids }
        self.log = logging.getLogger(__name__)
    
    def run(self):
        """
        Uses all UUIDs in database for ble devices, listens to each for a while,
        averages the datapoints, and inserts the data into the database.
        """
        self.log.info('Starting TiltHydrometerLogger.run')
        for uuid in self.uuids:
            self.listen(5, dt.timedelta(seconds=10), uuid)
        self.insert_data()

    def listen(self, data_points, duration, uuid):
        uuid_filter = IBeaconFilter(uuid=uuid)
        scanner = BeaconScanner(self.record_data, device_filter=uuid_filter)

        start_time = dt.datetime.now(pytz.utc)
        scanner.start()
        while dt.datetime.now(pytz.utc) - start_time < duration:
            if len(self.data[uuid]['T']) >= data_points:
                scanner.stop()
                break

    def record_data(self, bt_addr, rssi, packet, additional_info):
        timestamp = dt.datetime.now(pytz.utc)
        uuid = packet.uuid
        s = str(packet.minor)
        sg = float('{}.{}'.format(s[0:-3], s[-3:]))
        temp = packet.major
        print('Detected data: {}'.format(packet))
        self.data[uuid]['T'].append((timestamp, temp))
        self.data[uuid]['SG'].append((timestamp, sg))    

    def insert_data(self):
        for uuid in self.data.keys():
            logging_device = Device.objects.filter(uuid=uuid)
            if len(logging_device) > 1:
                raise ValueError('There are multiple devices with the same UUID in the database. Why?')
            elif len(logging_device) == 0:
                raise ValueError('There is no device in the DB with UUID {}'.format(uuid))
            else:
                logging_device = logging_device[0]

            t_dataset = Dataset.objects.filter(logging_device=logging_device, variable_measured='T')
            if len(t_dataset) > 1:
                raise ValueError('There are multiple T datasets currently associated with device UUID {}'.format(uuid))
            elif len(t_dataset) == 0:
                raise ValueError('There are no T datasets associated with device UUID {}'.format(uuid))
            else:
                t_dataset = t_dataset[0]

            sg_dataset = Dataset.objects.filter(logging_device=logging_device, variable_measured='SG')
            if len(sg_dataset) > 1:
                raise ValueError('There are multiple SG datasets currently associated with device UUID {}'.format(uuid))
            elif len(sg_dataset) == 0:
                raise ValueError('There are no SG datasets associated with device UUID {}'.format(uuid))
            else:
                sg_dataset = sg_dataset[0]

            for point in self.data[uuid]['T']:
                Datapoint.objects.create(timestamp=point[0], value=point[1], dataset=t_dataset)
            for point in self.data[uuid]['SG']:
                Datapoint.objects.create(timestamp=point[0], value=point[1], dataset=sg_dataset)


@task
def log_hydrometer_data():
    logger = TiltHydrometerLogger()
    logger.run()
