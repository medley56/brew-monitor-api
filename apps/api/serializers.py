from rest_framework import serializers
from apps.api.models import Datapoint, Dataset, Fermentation, Device, Control


class DatapointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Datapoint
        fields = ('id', 'timestamp', 'value', 'dataset')


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dataset
        fields = ('id', 'unit', 'variable_measured', 'fermentation', 'logging_device', 'controls', 'datapoints')


class ControlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Control
        fields = ('created', 'start_effect', 'end_effect', 'output_device', 'input_data', 'target_value')


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ('serial_number', 'uuid', 'name', 'type', 'datasets')


class FermentationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fermentation
        fields = ('id', 'name', 'datasets')
