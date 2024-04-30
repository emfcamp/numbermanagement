from django.urls import path
from . import views

urlpatterns = [
    path('api/list/<str:event>/<str:tos>', views.list_numbers, name='list'),
    path('api/number/<str:event>/<int:id>', views.get_number, name='list'),
    path('api/phonebook', views.phonebook, name='phonebook'),
    path('api/group/<str:event>/<int:group>', views.get_group, name='getgroup'),
    path('api/group/join/<str:event>/<int:group>', views.join_group, name='joingroup'),
    path('api/group/leave/<str:event>/<int:group>', views.leave_group, name='leavegroup'),

]