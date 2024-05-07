from django.urls import path
from . import views

urlpatterns = [
    path('', views.phonebook, name='phonebook'),
    path('phonebook', views.phonebook, name='phonebook'),
    path('number', views.my_numbers, name='number-list'),
    path('number/create', views.create_number, name='number-create'),
    path('number/edit/<int:id>/', views.edit_number, name='number-edit'),
    path('number/delete/<int:id>/', views.delete_number, name='number-delete'),
    path('number/info/<int:id>/', views.number_info, name='number-info'),
    path('about', views.about, name='about'),

]
