from django_filters import rest_framework as filters
from apps.api.models import Datapoint, Dataset, Fermentation, Control, Device


class DatapointFilter(filters.FilterSet):
    class Meta:
        model = Datapoint
        fields = {
            'value': ['lt', 'gt'],
            'timestamp': ['lt', 'gt'],
            'dataset__variable_measured': ['exact']
        }


class DatasetFilter(filters.FilterSet):
    class Meta:
        model = Dataset
        fields = ('active', 'variable_measured', 'unit')


class FermentationFilter(filters.FilterSet):
    class Meta:
        model = Fermentation
        fields = {
            'name': ['icontains'],
        }


class DeviceFilter(filters.FilterSet):
    class Meta:
        model = Device
        fields = {
            'name': ['exact', 'icontains'],
            'serial_number': ['exact', 'icontains'],
            'uuid': ['exact', 'icontains'],
            'type': ['exact']
        }


class ControlFilter(filters.FilterSet):
    class Meta:
        model = Control
        fields = {
            'created': ['exact', 'lte', 'gte'],
            'start_effect': ['exact', 'lte', 'gte'],
            'end_effect': ['exact', 'lte', 'gte'],
            'output_device__id': ['exact'],
            'input_data__id': ['exact']
        }
