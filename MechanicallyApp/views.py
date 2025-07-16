from .models import Manufacturer, Location, UserLocationAssignment, Vehicle
from .serializers import ManufacturerSerializer, LocationSerializer, UserNestedLocationAssignmentSerializer, VehicleCreateUpdateSerializer, VehicleRetrieveSerializer, VehicleListSerializer
from rest_framework import generics
from .permissions import IsStandard, IsManager, IsAdmin, IsSuperUser, IsMechanic, DisableOPTIONSMethod
from rest_framework.permissions import IsAuthenticated

#dodawać i edytować Manufacturera może administrator, reszta może wypisywać
class ManufacturerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    def get_permissions(self):
        if self.request.method=='POST':
            self.permission_classes=[IsAdmin]
        elif self.request.method=='GET':
            self.permission_classes=[IsAuthenticated]
        elif self.request.method=='OPTIONS':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

class ManufacturerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    def get_permissions(self):
        if self.request.method=='GET':
            self.permission_classes=[IsAuthenticated]
        elif self.request.method=='PUT' or self.request.method=='PATCH' or self.request.method=='DELETE':
            self.permission_classes=[IsAdmin]
        elif self.request.method=='OPTIONS':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

#dodawać, usuwać oraz modyfikować lokalizacje może administrator
#wypisywać wszystkie lokalizacje może menadżer i admin
class LocationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    def get_permissions(self):
        if self.request.method=='GET':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method=='POST':
            self.permission_classes=[IsAdmin]
        elif self.request.method=='OPTIONS':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()


class LocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    def get_permissions(self):
        if self.request.method=='GET':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method=='PUT' or self.request.method=='PATCH' or self.request.method=='DELETE':
            self.permission_classes=[IsAdmin]
        elif self.request.method=='OPTIONS':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

#informacje o swojej lokalizacji może wypisywać standard i mechanik
class UserLocationListAPIView(generics.ListAPIView):
    queryset = UserLocationAssignment.objects
    serializer_class = UserNestedLocationAssignmentSerializer
    def get_queryset(self):
        qs=super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method=='GET':
            self.permission_classes=[IsMechanic|IsStandard]
        elif self.request.method=='OPTIONS':
            self.permission_classes = [DisableOPTIONSMethod]
        return super().get_permissions()

class VehicleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleListSerializer
    def get_serializer_class(self):
        if self.request.method=='POST':
            return VehicleCreateUpdateSerializer
        return VehicleListSerializer

class VehicleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    def get_serializer_class(self):
        if self.request.method=='GET':
            return VehicleRetrieveSerializer
        return VehicleCreateUpdateSerializer
