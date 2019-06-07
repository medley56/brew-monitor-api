from django.db import models


class Fermentation(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return '{}'.format(self.name)


class Device(models.Model):
    DEVICE_TYPES = (
        ('GPIO', 'GPIO Device'),
        ('BLE', 'Bluetooth Low Energy Device'),
    )
    serial_number = models.CharField(max_length=100, null=True)
    uuid = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10,
        choices=DEVICE_TYPES
    )


class Dataset(models.Model):
    UNIT_CHOICES = (
        ('DEGC', 'Degrees Celcius'),
        ('DEGF', 'Degrees Farenheit'),
        ('UNITLESS', 'Unitless')
    )

    VARIABLE_MEASURED_CHOICES = (
        ('T', 'Temperature'),
        ('SG', 'Specific Gravity')
    )

    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES
    )

    variable_measured = models.CharField(
        max_length=10,
        choices=VARIABLE_MEASURED_CHOICES
    )

    # No sense having a dataset that's not associated with a fermentation => Required
    fermentation = models.ForeignKey(Fermentation, related_name='datasets', on_delete=models.CASCADE)

    # Null must be allowable so datasets can end and devices can go on logging to new datasets
    logging_device = models.ForeignKey(Device, null=True, related_name='datasets', on_delete=models.SET_NULL)

    def __str__(self):
        return '{} ({}) [id={}]'.format(self.get_variable_measured_display(), self.get_unit_display(), self.id)


class Datapoint(models.Model):
    timestamp = models.DateTimeField()
    value = models.DecimalField(decimal_places=8, max_digits=12)
    dataset = models.ForeignKey(Dataset, related_name='datapoints', on_delete=models.CASCADE)


class Control(models.Model):
    created = models.DateTimeField(auto_created=True)
    start_effect = models.DateTimeField()
    end_effect = models.DateTimeField()
    output_device = models.ForeignKey(Device, related_name='controls', on_delete=models.CASCADE)
    input_data = models.ForeignKey(Dataset, related_name='controls', on_delete=models.CASCADE)
    target_value = models.DecimalField(max_digits=12, decimal_places=8)
