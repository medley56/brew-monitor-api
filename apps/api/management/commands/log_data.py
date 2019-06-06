import pytz
import datetime as dt
from beacontools import BeaconScanner, IBeaconFilter
from django.core.management.base import BaseCommand, CommandError
from apps.api.models import Device, Fermentation, Dataset, Datapoint

class Command(BaseCommand):
    help = 'Extracts tilt device UUIDs from the database and logs incoming data.'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def __init__(self):
        super().__init__()
        print('Init-ing')
        if len(Device.objects.all()) == 0:
            raise ValueError('Must have at least one UUID to search for')
        self.uuids = [device.uuid for device in Device.objects.all()]
        self.data = { uuid: {'temp': [], 'sg': []} for uuid in self.uuids }
        print(self.uuids)

    def record_data(self, bt_addr, rssi, packet, additional_info):
        timestamp = dt.datetime.now(pytz.utc)
        uuid = packet.uuid
        s = str(packet.minor)
        sg = float('{}.{}'.format(s[0:-3], s[-3:]))
        temp = packet.major
        print('Detected data: {}'.format(packet))
        self.data[uuid]['temp'].append((timestamp, temp))
        self.data[uuid]['sg'].append((timestamp, sg))

    def add_data_to_db(self):
        for uuid in self.data.keys():
            logging_device = Device.objects.get(uuid=uuid)
            t_dataset = Dataset.objects.get(logging_device=logging_device, variable_measured='T')
            sg_dataset = Dataset.objects.get(logging_device=logging_device, variable_measured='SG')
            for point in self.data[uuid]['temp']:
                Datapoint.objects.create(timestamp=point[0], value=point[1], dataset=t_dataset)
            for point in self.data[uuid]['sg']:
                Datapoint.objects.create(timestamp=point[0], value=point[1], dataset=sg_dataset)

    def handle(self, *args, **options):
        print('Starting scan')
        for uuid in self.uuids:
            print('UUID: {}'.format(uuid))
            uuid_filter = IBeaconFilter(uuid=uuid)
            scanner = BeaconScanner(self.record_data, device_filter=uuid_filter)
            scanner.start()
            
            print(uuid)
            start = dt.datetime.now(pytz.utc)
            while dt.datetime.now(pytz.utc) - start < dt.timedelta(seconds=60):
                if len(self.data[uuid]['temp']) > 10:
                    scanner.stop()
                    break
        print(self.data)
        
        self.add_data_to_db()
