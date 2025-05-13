from django.urls import path
from . import views


app_name = 'booking'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='user-booking-list'),
    path('create', views.BookingCreateView.as_view(), name='create-booking'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    # path('bookings/<str:booking_code>/', apiviews.BookingDetailView.as_view(), name='booking-detail'),
    # path('api/<int:pk>/update/', apiviews.BookingUpdateView.as_view(), name='booking-update'),
    # path('api/<int:pk>/delete/', apiviews.BookingDestroyView.as_view(),
    #      name='booking-delete'),
]