from .models import Company, House, Apartment
from django.forms import ModelForm
from django import forms

class CompanyForm(forms.Form):
    name = forms.CharField(required=True, max_length=200)
    def clean_name(self):
        name = self.cleaned_data['name']
        if Company.objects.filter(name=name).exists():# проверка на наличие повторения названия компании
            raise forms.ValidationError("Company already exists")
        return name

class companyDetailsForm(forms.Form):
    address = forms.CharField(required=True, max_length=200)
    def clean_address(self):
        address = self.cleaned_data['address']
        if House.objects.filter(address=address).exists():# проверка на наличие повторения названия компании
            raise forms.ValidationError("Address already exists")
        return address

class houseDetailsForm(forms.Form):
    number = forms.IntegerField(label="номер квартиры:")
    open = forms.BooleanField(required=False)
    reaction = forms.IntegerField(required=False)
    name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=16, required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False)

