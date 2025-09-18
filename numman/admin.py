from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(TypeOfService)
admin.site.register(Number)
admin.site.register(Event)
admin.site.register(Range)
admin.site.register(Permission)


@admin.register(Reservation)
class ReservationsAdmin(admin.ModelAdmin):
    list_display = ['value', 'user', 'expiry', 'is_expired']
    list_filter = ['expiry', 'user']
    search_fields = ['value', 'user__username']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'