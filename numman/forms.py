from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model, Q
from django import forms
from django.forms.utils import ErrorList
from .models import Number, Event, TypeOfService, Range, Reservation
from django.core.exceptions import ValidationError
from django.utils import timezone
import json


class CreateNumberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateNumberForm, self).__init__(*args, **kwargs)
        
        # Your existing field setup
        self.fields['event'].queryset = Event.objects.filter(active=True)
        self.fields['typeofservice'].queryset = TypeOfService.objects.filter(privileged=False)
        self.fields['param'].label = ""
        self.fields['directory'].label = "Public Phonebook"
        self.fields['value'].label = "Number"
        self.fields['label'].label = "Description"
        self.fields['typeofservice'].label = "Type of Service"
        
        # Add dynamic fields based on typeofservice selection
        self._add_dynamic_fields()
    
    def _add_dynamic_fields(self):
        """Add dynamic fields based on user_data_schema"""
        # Get the initial typeofservice if this is a bound form or has initial data
        typeofservice = None
        
        if self.is_bound and 'typeofservice' in self.data:
            try:
                typeofservice_name = self.data['typeofservice']
                typeofservice = TypeOfService.objects.get(name=typeofservice_name)
            except TypeOfService.DoesNotExist:
                pass
        elif self.initial.get('typeofservice'):
            typeofservice = self.initial['typeofservice']
        elif hasattr(self.instance, 'typeofservice') and self.instance.typeofservice:
            typeofservice = self.instance.typeofservice
            
        if typeofservice and typeofservice.user_data_schema:
            try:
                schema = typeofservice.user_data_schema
                self._create_dynamic_fields(schema)
            except json.JSONDecodeError:
                pass
    
    def _create_dynamic_fields(self, schema):
        """Create form fields based on schema definition"""
        for field_name, field_config in schema.items():
            field_type = field_config.get('type', 'str')
            required = field_config.get('required', False)
            label = field_config.get('label', field_name.replace('_', ' ').title())
            
            # Create appropriate field type
            if field_type == 'str':
                field = forms.CharField(
                    required=required,
                    label=label,
                    max_length=field_config.get('max_length', 255)
                )
            elif field_type == 'int':
                field = forms.IntegerField(
                    required=required,
                    label=label
                )
            elif field_type == 'bool':
                field = forms.BooleanField(
                    required=required,
                    label=label
                )
            elif field_type == 'choice':
                choices = [(choice, choice) for choice in field_config.get('choices', [])]
                field = forms.ChoiceField(
                    choices=choices,
                    required=required,
                    label=label
                )
            else:
                # Default to CharField
                field = forms.CharField(
                    required=required,
                    label=label,
                    max_length=255
                )
            
            # Add the field with a prefix to avoid conflicts
            dynamic_field_name = f"user_data_{field_name}"
            self.fields[dynamic_field_name] = field
            
            # If editing an existing instance, populate with existing data
            if hasattr(self.instance, 'user_data') and self.instance.user_data:
                try:
                    existing_data = json.loads(self.instance.user_data)
                    if field_name in existing_data:
                        self.fields[dynamic_field_name].initial = existing_data[field_name]
                except json.JSONDecodeError:
                    pass

    def clean(self):
        super().clean()
        cd = self.cleaned_data
        print(cd)
        # Your existing validation logic
        number = int(cd.get("value"))
        user = getattr(self.instance, 'user', None)
        valid = False
        ranges = Range.objects.filter(privileged=False)
        active_reservation = Reservation.objects.filter(
            value=number
        ).filter(
            Q(expiry__isnull=True) | Q(expiry__gt=timezone.now())
        ).exclude(user=user).first()
        
        if active_reservation:
            raise ValidationError("Sorry this number is reserved by another user")
        
        for r in ranges:
            if r.start <= number <= r.end:
                valid = True
        
        if not valid:
            raise ValidationError("Number not in Valid Range")
        
        return cd
    
    def get_user_data(self):
        """Extract user data from cleaned_data and return as JSON string"""
        user_data = {}
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('user_data_'):
                # Remove the 'user_data_' prefix
                actual_field_name = field_name[10:]  # len('user_data_') = 10
                user_data[actual_field_name] = value
        
        return json.dumps(user_data) if user_data else None

    class Meta:
        model = Number
        fields = ['event', 'typeofservice', 'value', 'label', 'directory', 'param']


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