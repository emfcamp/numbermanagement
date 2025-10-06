from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model, Q
from django import forms
from django.forms.utils import ErrorList
from .models import Number, Event, TypeOfService, Range, Reservation
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
from audio_manager.models import AudioFile

def create_number_form_class(typeofservice=None, instance=None, edit=False, user=None):
    """Factory function that creates a form class with dynamic fields"""
    class DynamicCreateNumberForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.editMode = edit            
            self.fields['event'].queryset = Event.objects.filter(active=True)
            self.fields['typeofservice'].queryset = TypeOfService.objects.filter(privileged=False)
            self.fields['typeofservice'].label = "Type of Service"
            self.fields['typeofservice'].help_text = "The type of device or service this number will be using, see the wiki"
            self.fields['param'].label = " "
            self.fields['directory'].label = "Public Phonebook"
            self.fields['directory'].help_text = "Will the number be listed in the public phonebookt"
            self.fields['value'].label = "Number"
            self.fields['label'].label = "Description"
            if edit:
                self.fields['event'].disabled = True
                self.fields['param'].disabled = True
                self.fields['value'].disabled = True
                self.fields['typeofservice'].disabled = True
            # Set initial typeofservice if provided
            if typeofservice:
                self.fields['typeofservice'].initial = typeofservice
            else:
                self.fields['value'].widget = forms.HiddenInput()
                self.fields['label'].widget = forms.HiddenInput()
                self.fields['directory'].widget = forms.HiddenInput()
                self.fields['param'].widget = forms.HiddenInput()

        def full_clean(self):
            """Override full_clean to restore disabled fields before validation"""
            # Restore disabled field values from instance before validation runs
            if self.instance and self.instance.pk:
                # Check if we're in edit mode (disabled fields present)
                if self.editMode:
                    if 'event' not in self.data:
                        # Inject the instance values into self.data
                        # We need to make data mutable
                        if hasattr(self.data, '_mutable'):
                            self.data._mutable = True
                        # Restore values
                        if hasattr(self.instance, 'event') and self.instance.event:
                            self.data['event'] = str(self.instance.event.pk)
                        if hasattr(self.instance, 'typeofservice') and self.instance.typeofservice:
                            self.data['typeofservice'] = str(self.instance.typeofservice.pk)
                        if hasattr(self.instance, 'value'):
                            self.data['value'] = str(self.instance.value)
                        if hasattr(self.instance, 'param'):
                            self.data['param'] = str(self.instance.param)
                        if hasattr(self.data, '_mutable'):
                            self.data._mutable = False
            # Now run the normal validation
            super().full_clean()

        def clean(self):
            super().clean()
            cd = self.cleaned_data
            # Restore disabled fields from the instance
            if self.instance and self.instance.pk:
                if 'event' not in cd and hasattr(self.instance, 'event'):
                    cd['event'] = self.instance.event
                if 'typeofservice' not in cd and hasattr(self.instance, 'typeofservice'):
                    cd['typeofservice'] = self.instance.typeofservice
                if 'value' not in cd and hasattr(self.instance, 'value'):
                    cd['value'] = self.instance.value
                if 'param' not in cd and hasattr(self.instance, 'param'):
                    cd['param'] = self.instance.param
            
            number = int(cd.get("value"))
            user = getattr(self.instance, 'user', None)
            ranges = Range.objects.filter(privileged=False)
            active_reservation = Reservation.objects.filter(
                value=number
            ).filter(
                Q(expiry__isnull=True) | Q(expiry__gt=timezone.now())
            ).exclude(user=user).first()
            if active_reservation:
                raise ValidationError("Sorry this number is reserved by another user")
            valid = False
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
                    actual_field_name = field_name[10:]
                    user_data[actual_field_name] = value
            
            return json.dumps(user_data) if user_data else None

        class Meta:
            model = Number
            fields = ['event', 'typeofservice', 'value', 'label', 'directory', 'param']

    # Add dynamic fields if typeofservice is provided
    if typeofservice and typeofservice.user_data_schema:
        try:
            schema = json.loads(typeofservice.user_data_schema) if isinstance(typeofservice.user_data_schema, str) else typeofservice.user_data_schema
            # Get existing user data if we have an instance
            existing_user_data = {}
            if instance and hasattr(instance, 'user_data') and instance.user_data:
                try:
                    if isinstance(instance.user_data, str):
                        existing_user_data = json.loads(instance.user_data)
                    else:
                        existing_user_data = instance.user_data
                except (json.JSONDecodeError, TypeError):
                    existing_user_data = {}
            for field_name, field_config in schema.items():
                field_type = field_config.get('type', 'str')
                required = field_config.get('required', False)
                label = field_config.get('label', field_name.replace('_', ' ').title())
                # Get existing value for this field
                initial_value = existing_user_data.get(field_name)
                # Create appropriate field type
                if field_type == 'str':
                    field = forms.CharField(
                        required=required,
                        label=label,
                        max_length=field_config.get('max_length', 255),
                        initial=initial_value
                    )
                elif field_type == 'int':
                    field = forms.IntegerField(
                        required=required,
                        label=label,
                        initial=initial_value
                    )
                elif field_type == 'bool':
                    field = forms.BooleanField(
                        required=required,
                        label=label,
                        initial=bool(initial_value) if initial_value is not None else False
                    )
                elif field_type == 'choice':
                    choices = [('', '---------')] + [(choice, choice) for choice in field_config.get('choices', [])]
                    field = forms.ChoiceField(
                        choices=choices,
                        required=required,
                        label=label,
                        initial=initial_value
                    )
                elif field_type == 'media':
                    if user:
                        audio_files = AudioFile.objects.filter(user=user)
                        choices = [('', '---------')] + [(str(audio.file), audio.title) for audio in audio_files]
                    else:
                        choices = [('', '---------')]
                    field = forms.ChoiceField(
                        choices=choices,
                        required=required,
                        label=label,
                        initial=initial_value
                    )
                else:
                    # Default to CharField
                    field = forms.CharField(
                        required=required,
                        label=label,
                        max_length=255,
                        initial=initial_value
                    )
                # Add the field to the form class
                dynamic_field_name = f"user_data_{field_name}"
                DynamicCreateNumberForm.base_fields[dynamic_field_name] = field
                
        except (json.JSONDecodeError, TypeError):
            pass
    
    return DynamicCreateNumberForm



class DeleteNumberForm(forms.Form):
    checknumber = forms.CharField(label="Confirm the Number to Delete")