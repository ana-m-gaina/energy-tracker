from django.db import models
from django.urls import reverse
from django import forms
import uuid, requests, json
from datetime import timedelta, datetime


class GeodataTara(models.Model):
    id = models.BigAutoField(primary_key=True)
    surogate = models.CharField(max_length=150)
    name = models.CharField(max_length=40)

    class Meta:
        db_table = 'geodata_geodatatara'

    def __str__(self):
        return self.name

class GeodataJudet(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=125)
    abreviere = models.CharField(max_length=20)
    tara = models.ForeignKey(GeodataTara, models.DO_NOTHING)

    class Meta:
        db_table = 'geodata_geodajudet'

    def __str__(self):
        return self.name
    
class GeodataLocalitate(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=125)
    judet = models.ForeignKey(GeodataJudet, models.DO_NOTHING, blank=True, null=True)
    tara = models.ForeignKey(GeodataTara, models.DO_NOTHING, blank=True, null=True)
    latitude = models.CharField(max_length=7, blank=True, null=True)
    longitude = models.CharField(max_length=7, blank=True, null=True)

    class Meta:
        db_table = 'geodata_geodalocalitate'

    def __str__(self):
        return self.name

class GeodataStrada(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=125)
    judet = models.ForeignKey(GeodataJudet, models.DO_NOTHING)
    localitate = models.ForeignKey(GeodataLocalitate, models.DO_NOTHING)
    tara = models.ForeignKey(GeodataTara, models.DO_NOTHING)

    def __str__(self):
        return self.name



