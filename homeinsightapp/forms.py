from django.forms import ModelForm
from .models import *
from geodata.models import *
from django.forms import FileField, Form, ModelForm



class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['uuid', 'devices']

        labels = {
        "name":  "Name",
        "type": "Type",
        "year": "Year",
        "has_basement":  "Basement",
        "num_upper_floors":  "Building levels",
        "tara":  "Country",
        "judet":  "County",
        "localitate":  "City",
        "strada":  "Street",
        "numar":  "Street number",
        "bloc":  "Building number",
        "scara":  "Building entrance",
        "etaj":  "Unit level",
        "apartament":  "Apartment number",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['localitate'].queryset = GeodataLocalitate.objects.none()

        if 'judet' in self.data:
            try:
                judet_id = int(self.data.get('judet'))
                self.fields['localitate'].queryset =GeodataLocalitate.objects.filter(judet=judet_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Judet queryset
        elif self.instance.pk:
            self.fields['localitate'].queryset = self.instance.judet.localitate_set.order_by('name')


class DeviceForm(ModelForm):
    class Meta:
        model = Device
        exclude = ['profile', 'device_id']

        labels = {
        "name":  "Device name",
        }

class DeviceDataForm(ModelForm):
    class Meta:
        model = DeviceData
        exclude = ['value']
        prefix='index'
        

class UploadForm(Form):
    prefix='upload'
    data_file = FileField()
   






