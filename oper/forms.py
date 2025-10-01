from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model, Q
from django import forms
from django.forms.utils import ErrorList
from numman.models import Number, Event, TypeOfService, Range, Reservation
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from groups.models import Membership
from django.core.exceptions import ValidationError
from numman.models import Number
from django.utils import timezone
from django.utils import timezone
from datetime import timedelta


def create_number_form_class(typeofservice=None, instance=None, edit=False):
    """Factory function that creates a form class with dynamic fields"""
    class DynamicCreateNumberForm(forms.ModelForm):
        ignore_reservation = forms.BooleanField(
        required=False, 
        label="Override existing reservation",
        help_text="Check this box to use a number that's reserved by another user"
    )
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.editMode = edit            
            self.fields['event'].queryset = Event.objects.filter(active=True)
            self.fields['typeofservice'].queryset = TypeOfService.objects.filter(privileged=False)
            self.fields['param'].label = " "
            self.fields['directory'].label = "Public Phonebook"
            self.fields['value'].label = "Number"
            self.fields['label'].label = "Description"
            self.fields['typeofservice'].label = "Type of Service"
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
                self.fields['user'].widget = forms.HiddenInput()
                self.fields['permissions'].widget = forms.HiddenInput()
                self.fields['barred'].widget = forms.HiddenInput()
                self.fields['ignore_reservation'].widget = forms.HiddenInput()
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
            print(self.data)
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
            # Only check for reservations if ignore_reservation is False
            if not ignore_reservation:
                active_reservation = Reservation.objects.filter(
                    value=number
                ).filter(
                    Q(expiry__isnull=True) | Q(expiry__gt=timezone.now())
                ).exclude(user=user).select_related('user').first()
                if active_reservation:
                    username = active_reservation.user.username
                    if active_reservation.expiry:
                        expiry_str = active_reservation.expiry.strftime('%Y-%m-%d %H:%M')
                        error_msg = f"Sorry, this number is reserved for {username} until {expiry_str} UTC"
                    else:
                        error_msg = f"Sorry, this number is permanently reserved for {username}"
                    raise ValidationError(error_msg)
            # Range Validation
            valid = False
            ranges = Range.objects.filter(privileged=False)
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
            fields = ['event', 'typeofservice', 'value', 'label', 'directory', 'param', 'user', 'permissions', 'barred']

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


class CreateNumberForm(forms.ModelForm):
    ignore_reservation = forms.BooleanField(
        required=False, 
        label="Override existing reservation",
        help_text="Check this box to use a number that's reserved by another user"
    )
    
    def __init__(self, *args, **kwargs):
        super(CreateNumberForm, self).__init__(*args, **kwargs)
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
        user = cd.get("user")
        ignore_reservation = cd.get("ignore_reservation", False)
        valid = False
        ranges = Range.objects.filter()
        
        # Only check for reservations if ignore_reservation is False
        if not ignore_reservation:
            active_reservation = Reservation.objects.filter(
                value=number
            ).filter(
                Q(expiry__isnull=True) | Q(expiry__gt=timezone.now())
            ).exclude(user=user).select_related('user').first()
            if active_reservation:
                username = active_reservation.user.username
                if active_reservation.expiry:
                    expiry_str = active_reservation.expiry.strftime('%Y-%m-%d %H:%M')
                    error_msg = f"Sorry, this number is reserved for {username} until {expiry_str} UTC"
                else:
                    error_msg = f"Sorry, this number is permanently reserved for {username}"
                raise ValidationError(error_msg)
        # Range validation still applies regardless
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
        fields = ['label', 'directory', 'user', 'permissions', 'barred']


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
        self.fields['member'].queryset = Number.objects.filter(typeofservice__group_capable=True).order_by('value').filter(event=self.group.event).exclude(id__in=inner_qs)
        self.fields['delay'].widget = forms.Select(choices=(('0','0 Sec'),('20','20 Sec')))
    
    def clean(self):
        super().clean()
        cd = self.cleaned_data
        member = cd.get("member")
        number = Number.objects.select_related("typeofservice").filter(event=self.group.event).get(value=member)
        print(number)
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
