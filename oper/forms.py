from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model
from django import forms
from django.forms.utils import ErrorList
from numman.models import Number, Event, TypeOfService, Range
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from groups.models import Membership
from django.core.exceptions import ValidationError
from numman.models import Number


class CreateNumberForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (CreateNumberForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['event'].queryset = Event.objects.filter()
        self.fields['typeofservice'].queryset = TypeOfService.objects.filter()
        self.fields['param'].label = " "
        self.fields['directory'].label = "Phonebook"
        self.fields['value'].label = "Number"
        self.fields['label'].label = "Description"
        self.fields['typeofservice'].label = "Type of Service"

    def clean(self):
        super().clean()
        cd = self.cleaned_data
        number = int(cd.get("value"))
        valid = False
        ranges = Range.objects.filter()
        for r in ranges:
            if r.start <= number <= r.end:
                valid = True
        if not valid:
            raise ValidationError("Number not in Valid Range")
        return cd

    class Meta:
        model = Number
        fields = ['event', 'typeofservice', 'value', 'user', 'label', 'directory', 'permissions', 'param', 'barred']


class EditNumberForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (EditNumberForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['directory'].label = "Phonebook"
        self.fields['label'].label = "Description"
        self.fields['permissions'].required = False

    class Meta:
        model = Number
        fields = ['label', 'directory', 'user', 'permissions', 'barred', 'fwd_number']


class DeleteNumberForm(forms.Form):
    checknumber = forms.CharField(label="Confirm The Number to Delete")


class BlockUserForm(forms.Form):
    username = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
    is_active = forms.ChoiceField(choices = ((True, 'Not Blocked'), (False, 'Blocked')), label="Account State", initial='', widget=forms.Select(), required=True)


class JoinGroupForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        self.group = kwargs.pop('group')
        super (JoinGroupForm,self ).__init__(*args,**kwargs) # populates the post
        inner_qs = Membership.objects.filter(group=self.group).values('member')
        self.fields['member'].queryset = Number.objects.filter(typeofservice__group_capable=True).exclude(value__in=inner_qs)
        self.fields['delay'].widget = forms.Select(choices=(('0','0 Sec'),('20','20 Sec')))
    
    def clean(self):
        super().clean()
        cd = self.cleaned_data
        member = cd.get("member")
        number = Number.objects.select_related("typeofservice").get(value=member)
        tos = number.typeofservice
        currmembers =  Membership.objects.filter(group=self.group).all()
        print(len(currmembers))
        exists =  currmembers.filter(member=number).first()
        if exists:
            print("Number already in Group")
            raise ValidationError("Number already in Group")
        if tos.group_capable == False:
            print("Number is Not Group Capable")
            raise ValidationError("Number is Not Group Capable")
        print(cd)
        return cd


    class Meta:
        model = Membership
        fields = ['member', 'delay']
