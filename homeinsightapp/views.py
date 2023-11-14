from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from geodata.models import *
from django.http import JsonResponse, HttpResponse
from datetime import timedelta, date
from datetime import datetime
import pytz
from django.utils.timezone import make_aware
from dateutil import tz
import requests, csv
from dateutil import relativedelta
from .utils import *
from homeinsightprj.settings import TIME_ZONE
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.messages import constants


# AJAX city
def load_localitati(request):
    judet_id = request.GET.get('judet_id')
    localitati = GeodataLocalitate.objects.filter(judet=judet_id)
    return JsonResponse(list(localitati.values('id', 'name')), safe=False)

class Home(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/accounts/login/')
        return render( request,'index.html')

def guest(request):
    pk='2'
    email= 'demohomeinsight@gmail.com'
    password = '1234abcdZ'
    username = email
    try:
        user = CustomUser.objects.get(pk=pk)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/accounts/login/')
        else:
            raise PermissionDenied('404.html')
    except:
        raise PermissionDenied('404.html')


method_decorator(login_required, name='dispatch')
class ProfileList(View):
        def get(self, request, *args, **kwargs):
            profiles = request.user.profiles.all()
            context = {'profiles':profiles}
            return render(request, 'profilelist.html', context)

method_decorator(login_required, name='dispatch')
class ProfileCreate(View):
    def get(self, request, *args, **kwargs):
        form = ProfileForm()
        context = {'form':form}
        return render(request, 'profilecreate.html', context)

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None)
        if form.is_valid():
            if self.request.user.email == 'demohomeinsight@gmail.com':
                raise PermissionDenied('403.html')
            else:
                profile = Profile.objects.create(**form.cleaned_data)
                if profile:
                    request.user.profiles.add(profile)
                    return redirect('homeinsightapp:profile-list')
            context = {'form':form }
            #return render(request, 'test.html')
            return render(request, 'profilecreate.html', context)

method_decorator(login_required, name='dispatch')
class ProfileDetail(View):
    def get(self, request, profile_id, *args, **kwargs):
        context={}
       
        try:
            #profile
            profile = Profile.objects.get(uuid=profile_id)
            context ['profile'] = profile
            devices = Device.objects.filter(profile = profile )
            context ['devices'] = devices
            

            #weather
            city = getattr(profile, 'localitate')
            base_url = "https://api.openweathermap.org/data/2.5/weather?"
            api_key= "19d9ae24b443d99232c89f92a11494aa"
            url = base_url + "q=" + str(city) + "&appid=" + api_key +'&units=metric'
            response = requests.get(url)
           
            if response.status_code == 200:
                data = response.json()
                weather = {                    
                    'temperature': data['main']['temp'] ,
                    'wind': data['wind']['speed'],   
                    'description' :data['weather'][0]['description'],
                    'icon' :data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'] ,
                    'pressure': data['main']['pressure'] ,
                    }
                context ['weather'] = weather

            # geolocate(lat,lon):     
            lat = str(profile.localitate.latitude)
            lon = str(profile.localitate.longitude)
            while len(lat)<7:
                lat=lat+'0'
            while len(lon)<7:
                lon=lon+'0' 
            geo_querystring = {"lat": lat,"lon":lon}

            # weather station:   
            endDate = date.today()
            startDate = (endDate - timedelta(days=2))
            geo_url = "https://meteostat.p.rapidapi.com/stations/nearby"
            headers = {	"X-RapidAPI-Key": "56200b8a8fmsh7ad7e3fa66cb869p1eef94jsn860d2612c34f",
	                    "X-RapidAPI-Host": "meteostat.p.rapidapi.com" }

            geo_response = requests.request("GET", geo_url, headers=headers, params=geo_querystring)
            geo_data=geo_response.json()
            if geo_response.status_code == 200:
                station = geo_data['data'][0]

                # hourly station data: 
                hourly_url = "https://meteostat.p.rapidapi.com/stations/hourly"
                hourly_querystring = {"station":station['id'],"start":startDate,"end":endDate,"tz":"Europe/Bucharest"}
                hourly_response = requests.request("GET", hourly_url, headers=headers, params=hourly_querystring)
                hourly_data=hourly_response.json()
                hourly =  hourly_data['data']

                timeList=[]
                tempList=[]
                local= tz.gettz('Europe/Bucharest')
                utc_now = datetime.datetime.now()

                for i in range (0,len(hourly)-1):
                    utcTimeStamp=datetime.datetime.strptime(hourly[i]['time'],'%Y-%m-%d %H:%M:%S')
                    if utcTimeStamp  <= utc_now:
                        localtime =str( utcTimeStamp + timedelta(hours=2) )
                        timeList.append( localtime )
                        tempList.append( hourly[i]['temp'])
                    else:
                        lastElement= i
                        break

                context ['timeList'] = timeList
                context ['tempList'] = tempList

            #last year monthly mean
            series={}
            maxtimeseries=[]
            timeseriesList=[]
            lastDay_use= {}
            lastMonth_use= {}
            lastYear_use= {}
                
            count=0   
            for item in devices:
                device = Device.objects.get(device_id=item.device_id)
                device_data = DeviceData.objects.filter(device=device)
                usage = device_data.exclude(value__isnull=True).order_by("timestamp")
                if usage:
                    maxtimeseries.append (usage[len(usage)-1].timestamp)
                    last_day = get_dataset_ndays(usage, 1)
                    day_mean = get_mean(last_day,'D')[1]
                    if len(day_mean) > 1:
                        day_mean=day_mean[len(day_mean)-1]
                    lastDay_use[device.name] = day_mean
                        
                maxtimeseries.sort()
                try: 
                    time_end= maxtimeseries[len(maxtimeseries)-1]
                    time_start = time_end-relativedelta.relativedelta(months=11)
                    
                    while (count < 12) :
                        index = time_start.month + count
                       
                        if index > 11 :
                            index= index-12
                        months = month_converter(int(index))
                        timeseriesList.append(months)
                        count+=1
                    context['timeseriesList']=timeseriesList
                  
  
                    if usage:
                        last_year = usage.filter(timestamp__range=(time_start, time_end))
                        y_mean = get_mean(last_year,'M')     
                        series[device.name] = y_mean[1]  
            
                    context['series']=series
                    context ['max_daily_value'] = max(lastDay_use.values())
                    context ['max_daily_key'] = max(lastDay_use, key=lastDay_use.get)
                    
                    for key in series.keys():
                            lastMonth_use[key] = series[key][len(series[key])-1]
                            lastYear_use[key] = '%.3f'%(sum([float(x) for x in series[key]])/12)
                    context ['max_monthly_value'] = max(lastMonth_use.values())
                    context ['max_monthly_key'] = max(lastMonth_use, key=lastMonth_use.get)
                    context ['max_yearly_value'] = max(lastYear_use.values())
                    context ['max_yearly_key'] = max(lastYear_use, key=lastYear_use.get)
                except:
                    pass
                

            # print(f"Series: {context.get('timeseriesList')}")


            return render(request, 'dashboard.html', context)
        except Profile.DoesNotExist:
            return redirect('homeinsightapp:profile-list')

method_decorator(login_required, name='dispatch')
class ProfileInfo(View):
    def get(self, request, profile_id, *args, **kwargs):
        context={}
        try:
            #profile
            profile = Profile.objects.get(uuid=profile_id)
            context ['profile'] = profile
            devices = Device.objects.filter(profile = profile )
            context ['devices'] = devices
            return render(request, 'profile_info.html', context)
        except Profile.DoesNotExist:
            return redirect('homeinsightapp:profile-list')


method_decorator(login_required, name='dispatch')
class DeviceList(View):
    def get(self, request, profile_id, *args, **kwargs):
        context={}
        try:
            profile = Profile.objects.get(uuid=profile_id)
            context ['profile'] = profile
            devices = Device.objects.filter(profile = profile)
            context ['devices'] = devices
            form = DeviceForm()
            context ['form'] = form
            return render(request, 'devicelist.html', context)
        except Profile.DoesNotExist:
            return redirect('homeinsightapp:profile-list')
            
    def post(self, request, profile_id, *args, **kwargs):
        form = DeviceForm(request.POST or None)
        if form.is_valid():
            if self.request.user.email == 'demohomeinsight@gmail.com':
                raise PermissionDenied('403.html')
            else:
                device = Device.objects.create(**form.cleaned_data)
                if device:
                    context={}
                    profile = Profile.objects.get(uuid=profile_id)
                    context ['profile'] = profile
                    device.profile = profile
                    device.save()
                    devices = Device.objects.filter(profile = profile )
                    context ['devices'] = devices
                    form = DeviceForm()
                    context ['form'] = form
                    return render(request, 'devicelist.html', context)
        return render(request, 'devicelist.html', context)

method_decorator(login_required, name='dispatch')
class DeviceDetail(View):

    def get(self, request,profile_id, device_id, *args, **kwargs):
        context={}
        try:
            profile = Profile.objects.get(uuid=profile_id)
            context ['profile'] = profile
            devices = Device.objects.filter(profile = profile )
            context ['devices'] = devices
            device = Device.objects.get(device_id=device_id)
            context ['device'] = device
            device_data = DeviceData.objects.filter(device=device)
            form = DeviceDataForm(prefix='index')
            context ['form'] = form
            upload_form = UploadForm(prefix='upload')
            context ['upload_form'] = upload_form
           
            #indexes
            indexes= device_data.exclude(index__isnull=True)
            if (len(indexes)>0):
                if len(indexes)<2:
                    last_two = indexes
                else:
                    last_two = indexes[len(indexes)-2:len(indexes)]
                context ['last_two'] = last_two
                context ['indexes'] = indexes
            timeList=[]
            indexList=[]
            for point in indexes:
                timeList.append(str( utc_to_local(point.timestamp) ))
                indexList.append(int(point.index))
            context ['timeList'] = timeList
            context ['indexList'] = indexList

            #usage
            usage= device_data.exclude(value__isnull=True).order_by("timestamp") 
            if usage:

                #last entrys     
                if (len(usage)>0):
                    if len(usage)<4:
                        context ['last_five'] = usage[:len(usage)]
                    else:
                        context ['last_five'] = usage[len(usage)-5:len(usage):]
                
                #last 3 days hourly data
                n_days=3
                last_n_days = get_dataset_ndays(usage, n_days)
                context['n_days']=n_days
                context['last_n_days'] = last_n_days 
                context['last_n_days_timeList'] = make_timepoints(last_n_days )
               
                #last 30 days daily mean
                m_days=30
                context['m_days'] = m_days
                last_m_days = get_dataset_ndays(usage, m_days)
                d_mean = get_mean(last_m_days,'D')
                context['m_time'] = d_mean[0]
                context['m_value'] = d_mean[1]

                #last year mean
                l_date = usage[len(usage)-1].timestamp
                f_date = l_date-relativedelta.relativedelta(months=12)
                last_year = usage.filter(timestamp__range=(f_date, l_date))
                y_mean = get_mean(last_year,'M')           
                context['y_time'] = y_mean[0]
                context['y_value'] = y_mean[1]

            return render(request, 'device_detail.html', context)
        except Device.DoesNotExist:
            return redirect('homeinsightapp:profile-list')
    
    def post(self, request,profile_id, device_id, *args, **kwargs):
        context={}
        profile = Profile.objects.get(uuid=profile_id)
        context ['profile'] = profile
        device = Device.objects.get(device_id=device_id)
        context ['device'] = device
        form = DeviceDataForm(request.POST, prefix='index')
        upload_form = UploadForm(request.POST, request.FILES, prefix='upload')

        if self.request.user.email == 'demohomeinsight@gmail.com':
             raise PermissionDenied('403.html')
        else: 
            if 'index' in request.POST:
                if form.is_valid():
                    instance = DeviceData.objects.create(**form.cleaned_data)
                    instance.device = device
                    instance.timestamp = datetime.datetime.now(pytz.timezone(TIME_ZONE))
                    instance.index = form.cleaned_data['index']
                    instance.save()
                    context ['message'] = 'Index has been updated'
                else: 
                    context ['message'] = 'Invalid index'
                return render(request,'index_updated.html', context)
            elif 'upload' in request.POST:
                if upload_form.is_valid():
                    context['test']= 'test'
                    file= upload_form.cleaned_data['data_file']   
                    decoded_file  = file.read().decode("utf-8").splitlines()
                    keys=['time', 'value',]
                    reader = csv.DictReader(decoded_file, fieldnames=keys, delimiter=',', quoting=csv.QUOTE_NONE)
                    for row in reader:
                        try:
                            t_stp = row['time']
                            if t_stp:
                                try:
                                    v_stp = round(float(row['value']),5)
                                    if v_stp:
                                        instance = DeviceData.objects.create()
                                        instance.device = device
                                        instance.index=None
                                        instance.timestamp = t_stp
                                        instance.value = v_stp       
                                        instance.save() 
                                except:
                                    pass         
                        except:
                            pass
                    context ['message'] = 'Records have been updated'
                else: 
                    context ['message'] = 'Records inavlid'
                return render(request,'index_updated.html', context)
            else:
                return render(request, 'device_detail.html', context)


method_decorator(login_required, name='dispatch')
def index_updated(self, request,profile_id, device_id, *args, **kwargs):
    context={}
    profile = Profile.objects.get(uuid=profile_id)
    context ['profile'] = profile
    devices = Device.objects.filter(profile = profile )
    context ['devices'] = devices
    device = Device.objects.get(device_id=device_id)
    context ['device'] = device
    return render(request,'device-detail', context)




    
            


   






  





    














