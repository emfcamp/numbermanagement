from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model
from django import forms
from django.forms.utils import ErrorList
from .models import Number, Event, TypeOfService, Range
from django.core.exceptions import ValidationError

class CreateNumberForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (CreateNumberForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['event'].queryset = Event.objects.filter(active=True)
        self.fields['typeofservice'].queryset = TypeOfService.objects.filter(privileged=False)
        self.fields['param'].label = ""
        self.fields['directory'].label = "Public Phonebook"
        self.fields['value'].label = "Number"
        self.fields['label'].label = "Description"
        self.fields['typeofservice'].label = "Type of Service"

    def clean(self):
        super().clean()
        cd = self.cleaned_data
        number = int(cd.get("value"))
        valid = False
        ranges = Range.objects.filter(privileged=False)
        for r in ranges:
            if r.start <= number <= r.end:
                valid = True
        if not valid:
            raise ValidationError("Number not in Valid Range")
        return cd

    class Meta:
        model = Number
        fields = ['event', 'typeofservice', 'value', 'label', 'directory',  'param' ]


class EditNumberForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (EditNumberForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['directory'].label = "Public Phonebook"
        self.fields['label'].label = "Description "
        self.fields['fwd_number'].label = "Forward to"
        
    class Meta:
        model = Number
        fields = ['label', 'directory', 'fwd_number']


class DeleteNumberForm(forms.Form):
    checknumber = forms.CharField(label="Confirm the Number to Delete")