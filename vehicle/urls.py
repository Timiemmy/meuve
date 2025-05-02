from django.urls import path
from . import views 


urlpatterns = [
    path('', views.VehicleListView.as_view(), name='vehicle-list'),
    path('<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('create/', views.VehicleCreateWithImages.as_view(),
         name='vehicle-create'),
    path('update/<int:pk>/',
         views.VehicleUpdateWithImages.as_view(), name='vehicle-update'),
    path('delete/<int:pk>/',
         views.VehicleDeleteView.as_view(), name='vehicle-delete'),
    path('category', views.VehicleTypeListView.as_view(),
         name='vehicle-type-list'),
    path('category/create',
         views.VehicleTypeCreateView.as_view(), name='vehicle-type-create'),
    path('categorytype/<int:pk>/',
         views.VehicleTypeDetailView.as_view(), name='vehicle-type-detail'),
    path('category/delete/<int:pk>/',
         views.VehicleTypeDeleteView.as_view(), name='vehicle-type-delete'),
    path('amenity', views.VehicleAmenityListView.as_view(),
         name='vehicle-amenity-list'),
    path('amenity/create',
         views.VehicleAmenityCreateView.as_view(), name='vehicle-amenity-create'),
    path('amenity/<int:pk>/',
         views.VehicleAmenityDetailView.as_view(), name='vehicle-amenity-detail'),
    path('amenity/delete/<int:pk>/',
         views.VehicleAmenityDeleteView.as_view(), name='vehicle-amenity-delete'),
    path('image/create',
         views.VehicleImageListView.as_view(), name='vehicle-image-create'),
    path('image/<int:pk>/',
         views.VehicleImageDetailView.as_view(), name='vehicle-image-detail'),
]