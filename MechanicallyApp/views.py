from rest_framework.response import Response
from .models import Manufacturer, Location, UserLocationAssignment, Vehicle, User
from .serializers import ManufacturerSerializer, LocationSerializer, UserNestedLocationAssignmentSerializer, \
    VehicleCreateUpdateSerializer, VehicleRetrieveSerializer, VehicleListSerializer, AccountActivationSerializer, UserCreateSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from .permissions import IsStandard, IsManager, IsAdmin, IsSuperUser, IsMechanic, DisableOPTIONSMethod
from rest_framework.permissions import IsAuthenticated, AllowAny


#dodawać i edytować Manufacturera może administrator, reszta może wypisywać
class ManufacturerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    def get_permissions(self):
        if self.request.method.lower()=='post':
            self.permission_classes=[IsAdmin]
        elif self.request.method.lower()=='get':
            self.permission_classes=[IsAuthenticated]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

class ManufacturerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    def get_permissions(self):
        if self.request.method.lower()=='get':
            self.permission_classes=[IsAuthenticated]
        elif self.request.method.lower()=='put' or self.request.method.lower()=='patch' or self.request.method.lower()=='delete':
            self.permission_classes=[IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

#dodawać, usuwać oraz modyfikować lokalizacje może administrator
#wypisywać wszystkie lokalizacje może menadżer i admin
class LocationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    def get_permissions(self):
        if self.request.method.lower()=='get':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method.lower()=='post':
            self.permission_classes=[IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()


class LocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    def get_permissions(self):
        if self.request.method.lower()=='get':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method.lower()=='put' or self.request.method.lower()=='patch' or self.request.method.lower()=='delete':
            self.permission_classes=[IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

#informacje o swojej lokalizacji może wypisywać standard i mechanik
class UserLocationListAPIView(generics.ListAPIView):
    queryset = UserLocationAssignment.objects.all()
    serializer_class = UserNestedLocationAssignmentSerializer
    def get_queryset(self):
        qs=super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method.lower()=='get':
            self.permission_classes=[IsMechanic|IsStandard]
        elif self.request.method.lower()=='options':
            self.permission_classes = [DisableOPTIONSMethod]
        return super().get_permissions()

#ten widok umożliwia wypisywanie i tworzenie pojazdów przez menadżera oraz administratora
#za pomocą odpowiednich query setów muszę zaimplementować wypisywanie pojazdów z siedziby standarda
#a także wypisywanie pojazdów przez mechanika, dla których istnieje powiązanie FailureReport z jego warsztatem
class VehicleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleListSerializer

    def get_serializer_class(self):
        if self.request.method.lower()=='post':
            return VehicleCreateUpdateSerializer
        return VehicleListSerializer

    def get_permissions(self):
        if self.request.method.lower()=='get':
            self.permission_classes=[IsAuthenticated]
        elif self.request.method.lower()=='post':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

    def get_queryset(self):
        qs=super().get_queryset()
        if self.request.method=='GET':
            if self.request.user.role=='standard':
                standard_location=UserLocationAssignment.objects.get(user=self.request.user).location
                return qs.filter(location=standard_location)
            # TODO: zrobić test poprawnego działania w przypadku mechanika
            elif self.request.user.role=='mechanic':
                mechanic_location=UserLocationAssignment.objects.get(user=self.request.user).location
                return qs.filter(failure_reports__workshop=mechanic_location)
        return qs

#ten widok umożliwia menadżerowi oraz administratorowi odczytywanie, aktualizowanie oraz usuwanie pojazdu
class VehicleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    def get_serializer_class(self):
        if self.request.method.lower()=='get':
            return VehicleRetrieveSerializer
        return VehicleCreateUpdateSerializer

    def get_permissions(self):
        if self.request.method.lower()=='put' or self.request.method.lower()=='patch' or self.request.method.lower()=='delete':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

    def get_queryset(self):
        qs=super().get_queryset()
        if self.request.method.lower()=='get':
            if self.request.user.role=='standard':
                standard_location=UserLocationAssignment.objects.get(user=self.request.user).location
                return qs.filter(location=standard_location)
            elif self.request.user.role=='mechanic':
                mechanic_location=UserLocationAssignment.objects.get(user=self.request.user).location
                return qs.filter(failure_reports__workshop=mechanic_location)
        return qs

#jest to widok służący do aktywacji konta oraz zmiany hasła z domyślnego na wybrane przez usera
#TODO: przetestować poprawność działania
class AccountActivationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = AccountActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result=serializer.save()
        return Response({'result':result}, status=status.HTTP_200_OK)


#Jest to widok służący do utworzenia konta użytkownika. W zależności, czy użytkownik wysyłający request jest adminem czy superuserem, może on przydzielić inne role
#TODO: przetestować poprawność działania wraz z procesem aktywacji konta
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdmin]
    def get_serializer_context(self):
        context=super().get_serializer_context()
        context['is_superuser']=self.request.user.is_superuser
        return context


