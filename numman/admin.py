from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(TypeOfService)
admin.site.register(Number)
admin.site.register(Event)
admin.site.register(Range)
admin.site.register(Permission)