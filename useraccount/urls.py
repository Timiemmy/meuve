from django.urls import path
from . import views


app_name = 'user'

urlpatterns = [
    path('', views.CustomUserListView.as_view(), name='user-list'),
    path('create', views.CustomUserCreateView.as_view(), name='user-create'),
    path('<str:pk>', views.CustomUserDetailView.as_view(), name='user-detail'),
    path('<str:pk>/update',
         views.CustomUserUpdateView.as_view(), name='user-update'),
    path('<int:pk>/delete',
         views.CustomUserDestroyView.as_view(), name='user-delete'),

    path('driver', views.DriverListView.as_view(), name='driver_list'),

    path('emergency/', views.EmergencyContactListView.as_view(),
         name='emergency-list'),
    path('emergency/create',
         views.EmergencyContactCreateView.as_view(), name='emergency-create'),
    path('api/emergency/<int:emergency_pk>/delete',
         views.EmergencyContactDeleteView.as_view(), name='emergency-delete'),

    path('<int:pk>/address',
         views.AddressCreateView.as_view(), name='address-create'),
    path('<int:pk>/address/<int:address_pk>',
         views.AddressDetailView.as_view(), name='address-detail'),
    path('<int:pk>/address/<int:address_pk>/delete',
         views.AddressDeleteView.as_view(), name='address-delete'),
]
