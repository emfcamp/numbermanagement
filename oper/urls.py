from django.urls import path
from . import views

urlpatterns = [
    path('operator/', views.home, name='posts'),
    path('operator/number', views.my_numbers, name='number-list'),
    path('operator/number/create', views.create_number, name='number-create'),
    path('operator/number/edit/<int:id>/', views.edit_number, name='number-edit'),
    path('operator/number/delete/<int:id>/', views.delete_number, name='number-delete'),
    path('operator/user/block', views.block_user, name='user-block'),
    path('operator/groups', views.list_groups, name='list-group'),
    path('operator/group/<int:id>', views.manage_group, name='manage-group'),
    path('operator/group/remove/<int:gid>/<int:mid>', views.leave_group, name='leave-group'),
    path('operator/reservations', views.list_reservations, name='list-reservations'),
    path('operator/reservations/cleanup', views.cleanup_expired, name='cleanup-reservations')

]