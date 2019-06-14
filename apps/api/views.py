from rest_framework import viewsets
from apps.api.models import Datapoint, Dataset, Fermentation, Device, Control
from apps.api.serializers import \
    DatapointSerializer, DatasetSerializer, FermentationSerializer, DeviceSerializer, ControlSerializer
from apps.api.filters import DatapointFilter, DatasetFilter, DeviceFilter, FermentationFilter, ControlFilter


class DatapointViewSet(viewsets.ModelViewSet):
    queryset = Datapoint.objects.all()
    serializer_class = DatapointSerializer
    filterset_class = DatapointFilter


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    filterset_class = DatasetFilter


class FermentationViewSet(viewsets.ModelViewSet):
    queryset = Fermentation.objects.all()
    serializer_class = FermentationSerializer
    filterset_class = FermentationFilter


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filterset_class = DeviceFilter


class ControlViewSet(viewsets.ModelViewSet):
    queryset = Control.objects.all()
    serializer_class = ControlSerializer
    filterset_class = ControlFilter
