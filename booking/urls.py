from django.urls import path
from .api import views as apiviews


app_name = 'booking'

urlpatterns = [
    path('api/', apiviews.BookingListView.as_view(), name='user-booking-list'),
    path('api/create', apiviews.BookingCreateView.as_view(), name='create-booking'),
    path('api/<int:pk>/', apiviews.BookingDetailView.as_view(), name='booking-detail'),
    # path('bookings/<str:booking_code>/', apiviews.BookingDetailView.as_view(), name='booking-detail'),
    # path('api/<int:pk>/update/', apiviews.BookingUpdateView.as_view(), name='booking-update'),
    # path('api/<int:pk>/delete/', apiviews.BookingDestroyView.as_view(),
    #      name='booking-delete'),
]