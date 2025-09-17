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
        self.fields['member'].queryset = Number.objects.filter(typeofservice__group_capable=True).filter(event=self.group.event).exclude(id__in=inner_qs).order_by('value')
        self.fields['delay'].widget = forms.Select(choices=(('0','0 Sec'),('20','20 Sec')))
    
    def clean(self):
        super().clean()
        cd = self.cleaned_data
        member = cd.get("member")
        print(member)
        number = Number.objects.select_related("typeofservice").filter(event=self.group.event).get(value=member)
        tos = number.typeofservice
        currmembers =  Membership.objects.filter(group=self.group).all()
        exists =  currmembers.filter(member=number).first()
        if number.event != self.group.event:
            print("Number/Group event missmatch")
            raise ValidationError("Number is not for same event as Group")
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
