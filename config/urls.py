"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from allauth.account.views import ConfirmEmailView
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("dj_rest_auth.urls")),
    # Custom authentication URLs
    path('auth/', include('authentication.urls', namespace='auth')),

    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('user/', include('useraccount.urls', namespace='user')),
    path('park/', include('park.urls', namespace='park')),
    path('vehicle/', include('vehicle.urls')),
    path('booking/', include('booking.urls', namespace='booking')),
    path('payment/', include('payment.urls', namespace='payment')),

    # API Schema URLs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
