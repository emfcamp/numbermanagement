from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model
from django import forms
from django.forms.utils import ErrorList
from .models import Membership
from django.core.exceptions import ValidationError
from numman.models import Number

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
