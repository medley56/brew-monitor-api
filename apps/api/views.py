from rest_framework import viewsets
from apps.api.models import Datapoint, Dataset, Fermentation, Device, Control
from apps.api.serializers import DatapointSerializer, DatasetSerializer, FermentationSerializer, DeviceSerializer, ControlSerializer


class DatapointViewSet(viewsets.ModelViewSet):
    queryset = Datapoint.objects.all()
    serializer_class = DatapointSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer


class FermentationViewSet(viewsets.ModelViewSet):
    queryset = Fermentation.objects.all()
    serializer_class = FermentationSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class ControlViewSet(viewsets.ModelViewSet):
    queryset = Control.objects.all()
    serializer_class = ControlSerializer
