from django.urls import path
from .api import views as apiview


app_name = 'auth'

urlpatterns = [
    path('api/verify-email/', apiview.VerifyEmailCodeView.as_view(),
         name='verify-email'),
]