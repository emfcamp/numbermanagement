from django.contrib import admin
from .models import Group, Membership

# Register your models here.
admin.site.register(Group)
admin.site.register(Membership)