from django_filters import rest_framework as filters
from .models import Location, Vehicle, User, FailureReport, RepairReport, RepairReportRejection, Manufacturer, City


class LocationFilter(filters.FilterSet):
    class Meta:
        model = Location
        fields = {
            'name': ['icontains'],
            'location_type':['exact'],
        }

class ManufacturerFilter(filters.FilterSet):
    class Meta:
        model = Manufacturer
        fields = {
            'name': ['icontains'],
        }

class CityFilter(filters.FilterSet):
    class Meta:
        model = City
        fields = {
            'name': ['icontains'],
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

class FailureReportFilter(filters.FilterSet):
    vehicle=filters.UUIDFilter(field_name='vehicle', lookup_expr='exact')
    managed_by=filters.UUIDFilter(field_name='managed_by', lookup_expr='exact')
    class Meta:
        model = FailureReport
        fields = {
            'title': ['icontains'],
            'status': ['exact'],
        }

class RepairReportFilter(filters.FilterSet):
    vehicle=filters.UUIDFilter(field_name='failure_report__vehicle_id', lookup_expr='exact')
    title=filters.CharFilter(field_name='failure_report__title', lookup_expr='icontains')
    class Meta:
        model = RepairReport
        fields = {
            'status': ['exact'],
        }

class RepairReportRejectionFilter(filters.FilterSet):
    repair_report=filters.UUIDFilter(field_name='repair_report', lookup_expr='exact')
    class Meta:
        model = RepairReportRejection
        fields={
            'title': ['icontains'],
        }
