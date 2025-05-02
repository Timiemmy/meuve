from django.urls import path
from . import views 


app_name = 'park'

urlpatterns = [
    path('', views.ParkListView.as_view(), name='api_park_list'),
    path('<int:pk>/', views.ParkDetailView.as_view(), name='api_park_detail'),
]