from django.urls import path
from .views import PaymentCreateView, VerifyPaymentView

app_name = 'payment'

urlpatterns = [
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('verify/<str:reference>/',
         VerifyPaymentView.as_view(), name='payment-verify'),
]
