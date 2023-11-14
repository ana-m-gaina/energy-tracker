from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import datetime, date
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from geodata.models import *

#variables

TYPE_CHOICES = (
    ('Single house', 'Single house'),
    ('Duplex', 'Duplex'),
    ('Triplex', 'Triplex'),
    ('Row house', 'Row house'),
    ('Apartment', 'Apartment'),
)

CHOICES_BOOLEAN = (
    (True, ('Yes')),
    (False, ('No'))
)

UPPER_FLOOR_CHOICES = [(i, i) for i in range(1, 20)]

today=date.today()
current_year= today.year


#models

class CustomUser(AbstractUser):
    profiles = models.ManyToManyField('Profile', blank=True)

class Profile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=1000)
    type = models.CharField(choices=TYPE_CHOICES, max_length=25, null=True, blank=True)
    year = models.IntegerField(('year'), validators= [MinValueValidator(1800), MaxValueValidator(current_year)],null=True, blank=True)
    has_basement = models.BooleanField(choices=CHOICES_BOOLEAN, default=False, null=True)
    num_upper_floors = models.IntegerField(choices=UPPER_FLOOR_CHOICES, default=0, null=True)
    tara = models.ForeignKey(GeodataTara, on_delete=models.SET_NULL,blank=True,null=True)
    judet = models.ForeignKey(GeodataJudet, on_delete=models.SET_NULL,blank=True, null=True)
    localitate = models.ForeignKey(GeodataLocalitate, on_delete=models.SET_NULL,blank=True, null=True)
    strada = models.CharField(max_length=124, blank=True, null=True)
    numar=models.CharField(max_length=124, blank=True, null=True)
    bloc=models.CharField(max_length=124, blank=True, null=True)
    scara=models.CharField(max_length=124, blank=True, null=True)
    etaj=models.CharField(max_length=124, blank=True, null=True)
    apartament=models.CharField(max_length=124, blank=True, null=True)

    def __str__(self):
        return self.name

class Device(models.Model):
    device_id = models.UUIDField(default=uuid.uuid4)
    profile=models.ForeignKey(Profile, on_delete=models.SET_NULL,blank=True,null=True)
    name = models.CharField(max_length=124)

    def __str__(self):
        return self.name

class DeviceData(models.Model):    
    device=models.ForeignKey(Device, on_delete=models.SET_NULL,blank=True,null=True)
    timestamp = models.DateTimeField (blank=True, null=True)
    index = models.FloatField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)

