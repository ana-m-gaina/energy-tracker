from django.urls import path
from .views import *
from django.urls import path

app_name='homeinsightapp'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('guest/', guest, name="guest"),
    path('profiles/', ProfileList.as_view(), name="profile-list"),
    path('profiles/create/', ProfileCreate.as_view(), name="profile-create"),
    path('ajax/load-localitati/', load_localitati, name='ajax_load_localitati'),
    path('profiles/<str:profile_id>/', ProfileDetail.as_view(), name="dashboard"),
    path('profiles/<str:profile_id>/devices/', DeviceList.as_view(), name="devicelist"),
    path('profiles/<str:profile_id>/devices/<str:device_id>/', DeviceDetail.as_view(), name="device-detail"),
    path('profiles/<str:profile_id>/devices/<str:device_id>/submit_index', index_updated, name="index_updated"),
    ]


