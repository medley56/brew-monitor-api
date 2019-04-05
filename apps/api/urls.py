from django.urls import path, include
from rest_framework import routers
from apps.api import views


router = routers.DefaultRouter()
router.register(r'datapoints', views.DatapointViewSet)
router.register(r'datasets', views.DatasetViewSet)
router.register(r'fermentations', views.FermentationViewSet)
router.register(r'devices', views.DeviceViewSet)
router.register(r'controls', views.ControlViewSet)

urlpatterns = [
    path('', include(router.urls)),
]