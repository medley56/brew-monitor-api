import time
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
        self.data = {}
        self.uuids = [device.uuid for device in Device.objects.all()]
        if len(Device.objects.all()) == 0:
            raise ValueError('Must have at least one UUID to search for')
        print(self.uuids)

    def ingest_data(self, bt_addr, rssi, packet, additional_info):
        uuid = packet.uuid
        sg = packet.minor
        temp = packet.major
        print('I want to ingest this data: {}'.format(packet))
        if uuid in  self.data.keys():
            self.data[uuid]['temp'].append(temp)
            self.data[uuid]['sg'].append(sg)
        else:
            self.data[uuid] = {'temp': [temp], 'sg': [sg]}

    def handle(self, *args, **options):
        print('Starting scanner loop')
        for uuid in self.uuids:
            print('UUID: {}'.format(uuid))
            uuid_filter = IBeaconFilter(uuid=uuid)
            scanner = BeaconScanner(self.ingest_data, device_filter=uuid_filter)
            scanner.start()
            time.sleep(10)
            scanner.stop()
        print(self.data)
