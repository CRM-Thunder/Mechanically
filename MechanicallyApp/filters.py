from django_filters import rest_framework as filters
from .models import Location, Vehicle, User


class LocationFilter(filters.FilterSet):
    class Meta:
        model = Location
        fields = {
            'name': ['icontains'],
            'location_type':['exact'],
        }

class VehicleFilter(filters.FilterSet):
    manufacturer=filters.UUIDFilter(field_name='manufacturer',lookup_expr='exact')
    location=filters.UUIDFilter(field_name='location',lookup_expr='exact')
    class Meta:
        model = Vehicle
        fields = {
            'vehicle_model': ['icontains'],
            'year': ['exact', 'lt', 'gt', 'range'],
            'fuel_type': ['exact'],
            'availability': ['exact'],
            'vehicle_type': ['exact'],
        }

class UserFilter(filters.FilterSet):
    location=filters.UUIDFilter(field_name='user_location_assignment__location_id', lookup_expr='exact')
    role=filters.CharFilter(field_name='role', lookup_expr='exact')
    class Meta:
        model = User
        fields = {
            'first_name': ['icontains'],
            'last_name': ['icontains'],
            'email': ['icontains'],
            'phone_number': ['exact'],
        }