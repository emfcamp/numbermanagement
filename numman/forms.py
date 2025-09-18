from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model, Q
from django import forms
from django.forms.utils import ErrorList
from .models import Number, Event, TypeOfService, Range, Reservation
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        user = getattr(self.instance, 'user', None)
        valid = False
        ranges = Range.objects.filter(privileged=False)
        active_reservation = Reservation.objects.filter(
            value=number
        ).filter(
            Q(expiry__isnull=True) | Q(expiry__gt=timezone.now())
        ).exclude(user=user).first()
        if  active_reservation:
            raise ValidationError("Sorry this number is reserved by another user")
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
        self.fields['fwd_number'].label = "Fallback Number"
        
    class Meta:
        model = Number
        fields = ['label', 'directory', 'fwd_number']


class DeleteNumberForm(forms.Form):
    checknumber = forms.CharField(label="Confirm the Number to Delete")