from django.urls import path
from . import views

urlpatterns = [
    path('groups', views.list_groups, name='list-group'),
    path('group/<int:id>', views.manage_group, name='manage-group'),
    path('group/lookup/<str:eventvalue>', views.lookup_group, name='lookup-group'),
    path('group/remove/<int:gid>/<int:mid>', views.leave_group, name='leave-group'),
    path('group/membership/<int:id>', views.number_membership, name='number-membership')
]