from django.urls import path
from . import views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('manufacturers/',views.ManufacturerListCreateAPIView.as_view(), name='manufacturer-list'),
    path('manufacturers/<uuid:pk>/',views.ManufacturerRetrieveUpdateDestroyAPIView.as_view(), name='manufacturer-detail'),
    path('locations/',views.LocationListCreateAPIView.as_view(), name='location-list'),
    path('locations/<uuid:pk>/',views.LocationRetrieveUpdateDestroyAPIView.as_view(), name='location-detail'),
    path('my-location/',views.UserLocationListAPIView.as_view(), name='assigned-location'),
    path('vehicles/',views.VehicleListCreateAPIView.as_view(), name='vehicle-list'),
    path('vehicles/<uuid:pk>/',views.VehicleRetrieveUpdateDestroyAPIView.as_view(), name='vehicle-detail'),
    path('account/activate/', views.AccountActivationAPIView.as_view(), name='account-activation'),
    path('account/create/', views.UserCreateAPIView.as_view(), name='account-create'),
]