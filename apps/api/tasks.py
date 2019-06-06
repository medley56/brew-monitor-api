import pytz
import datetime as dt

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
    
    def run(self):
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
                break;

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
            logging_device = Device.objects.get(uuid=uuid)
            t_dataset = Dataset.objects.get(logging_device=logging_device, variable_measured='T')
            sg_dataset = Dataset.objects.get(logging_device=logging_device, variable_measured='SG')
            for point in self.data[uuid]['T']:
                Datapoint.objects.create(timestamp=point[0], value=point[1], dataset=t_dataset)
            for point in self.data[uuid]['SG']:
                Datapoint.objects.create(timestamp=point[0], value=point[1], dataset=sg_dataset)


@task
def log_hydrometer_data():
    logger = TiltHydrometerLogger()
    logger.run()
