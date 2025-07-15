from .models import Manufacturer, Location, UserLocationAssignment
from .serializers import ManufacturerSerializer, LocationSerializer, UserNestedLocationAssignmentSerializer
from rest_framework import generics

#dodawać i edytować Manufacturera może administrator, reszta może wypisywać
class ManufacturerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

class ManufacturerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

#dodawać, usuwać oraz modyfikować lokalizacje może administrator
#wypisywać wszystkie lokalizacje może menadżer i admin
class LocationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class LocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

#informacje o swojej lokalizacji może wypisywać standard i mechanik
class UserLocationRetrieveAPIView(generics.RetrieveAPIView):
    queryset = UserLocationAssignment.objects
    serializer_class = UserNestedLocationAssignmentSerializer
    def get_queryset(self):
        qs=super().get_queryset()
        return qs.filter(user=self.request.user)