from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def get_types():
    TYPES = {
        ("PWG", "Generated Password"),
        ("PWU", "User Password"),
        ("ACT", "Generated Activation Code"),
        ("NUM", "User Entered Number"),
        ("MAC", "User Entered MAC"),
        ("TXT", "User Entered Text"),
        ("UID", "UserID"),
    }
    return TYPES

class TypeOfService(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    privileged = models.BooleanField()
    param_type = models.CharField(max_length=3, choices=get_types)
    param_length = models.SmallIntegerField()
    param_name = models.CharField(max_length=32)
    group_capable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    active = models.BooleanField()

    def __str__(self):
        return self.name

class Permission(models.Model):
    value = models.CharField(max_length=32)
    
    def __str__(self):
        return self.value
    
class Number(models.Model):
    value = models.CharField(max_length=4, primary_key=True)
    label = models.CharField(max_length=32)
    typeofservice = models.ForeignKey(TypeOfService, on_delete=models.CASCADE)
    pub_date = models.DateTimeField("date published", default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    directory = models.BooleanField(default=False, choices=((True, 'List in Public Phonebook'), (False, 'Not Listed')))
    param = models.CharField(max_length=32)
    permissions = models.ManyToManyField(Permission)
    barred = models.BooleanField(default=False, choices=((True, 'Yes'), (False, 'No')))
    fwd_number = models.CharField(blank=True, max_length=16)

    def __str__(self):
        return self.value

class Range(models.Model):
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    privileged = models.BooleanField()


