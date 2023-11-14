from django.contrib import admin
from homeinsightapp.models import CustomUser, Profile, Device

admin.site.register(Profile)
admin.site.register(CustomUser)
admin.site.register(Device)


