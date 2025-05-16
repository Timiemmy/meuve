from django.urls import path
from . import views


app_name = 'auth'

urlpatterns = [
    path('verify-email/', views.VerifyEmailCodeView.as_view(),
         name='verify-email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(),
         name='resend-verification'),
]
