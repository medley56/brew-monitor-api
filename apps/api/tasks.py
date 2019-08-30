import pytz
import datetime as dt
from time import sleep

from beacontools import IBeaconFilter, BeaconScanner
from apps.api.models import Datapoint, Dataset, Device, Fermentation
from core import celery_app
from celery.utils.log import get_task_logger


class TiltHydrometerLogger(object):
    """
    Manages logging and data insertion for tilt hydrometer
    """

    def __init__(self):
        ble_devices = Device.objects.filter(type='BLE')
        if len(ble_devices) == 0:
            raise ValueError('No bluetooth devices found in database.')
        self.uuids = [device.uuid for device in ble_devices]
        self.data = {uuid: {'T': [], 'SG': []} for uuid in self.uuids}
        self.log = get_task_logger(__name__)

    def listen(self, uuid, duration):
        uuid_filter = IBeaconFilter(uuid=uuid)
        scanner = BeaconScanner(self.record_data, device_filter=uuid_filter)

        start_time = dt.datetime.now(pytz.utc)
        self.log.info('Listening for BLE beacons for {}s'.format(duration))
        scanner.start()
        while dt.datetime.now(pytz.utc) - start_time < duration:
            sleep(1)
        scanner.stop()
        self.log.info('Recorded {} temperature readings and {} gravity readings'
                      .format(len(self.data[uuid]['T']), len(self.data[uuid]['SG'])))

    def record_data(self, bt_addr, rssi, packet, additional_info):
        uuid = packet.uuid
        s = str(packet.minor)
        sg = float('{}.{}'.format(s[0:-3], s[-3:]))
        temp = float(packet.major)
        print('Detected data: {}'.format(packet))
        self.data[uuid]['T'].append(temp)
        self.data[uuid]['SG'].append(sg)

    def insert_data(self):
        for uuid in self.data.keys():
            if len(self.data[uuid]['T']) == 0 or len(self.data[uuid]['SG']) == 0:
                self.log.warning('Did not find any data from UUID {}'.format(uuid))
                continue
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

            avg_temp = sum(self.data[uuid]['T']) / len(self.data[uuid]['T'])
            avg_sg = sum(self.data[uuid]['SG']) / len(self.data[uuid]['SG'])
            now = dt.datetime.now(pytz.utc)

            Datapoint.objects.create(timestamp=now, value=avg_temp, dataset=t_dataset)
            Datapoint.objects.create(timestamp=now, value=avg_sg, dataset=sg_dataset)
            self.log.info('Saved averaged data for SG and temp at {}'.format(now))


@celery_app.task
def log_hydrometer_data():
    logger = TiltHydrometerLogger()
    for uuid in logger.uuids:
        logger.listen(uuid, dt.timedelta(seconds=30))
    logger.insert_data()


celery_app.register_task(log_hydrometer_data)
