from django.contrib import admin
from apps.api.models import Fermentation, Device, Dataset, Datapoint, Control
# Register your models here.

admin.site.register([Fermentation, Device, Dataset, Datapoint, Control])
