from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Manufacturer, Location, UserLocationAssignment, Vehicle, User, FailureReport
from .serializers import ManufacturerSerializer, LocationSerializer, UserNestedLocationAssignmentSerializer, \
VehicleCreateUpdateSerializer, VehicleRetrieveSerializer, VehicleListSerializer, AccountActivationSerializer, \
UserCreateSerializer, UserListSerializer,UserUpdateSerializer, ResetPasswordSerializer, ResetPasswordRequestSerializer, \
UserRetrieveSerializer, UserLocationAssignmentSerializer, FailureReportCreateSerializer, FailureReportListSerializer, \
FailureReportRetrieveSerializer, FailureReportAssignWorkshopSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from .permissions import IsStandard, IsManager, IsAdmin, IsMechanic, DisableOPTIONSMethod, IsAdminOrSuperuserAndTargetUserHasLowerRole
from rest_framework.permissions import IsAuthenticated


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
        elif self.request.method.lower() in ('put','patch','delete'):
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
        elif self.request.method.lower() in ('put','patch','delete'):
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
        if self.request.method.lower() in ('put','patch','delete'):
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
    permission_classes = [~IsAuthenticated]

    def post(self,request):
        serializer = AccountActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result=serializer.save()
        return Response({'result':result}, status=status.HTTP_200_OK)

#TODO: przetestować workflow resetu hasła, w przyszłości dodać throttling aby uniknąć DoS
#widok służący do wysyłania email w związku z żądaniem resetu hasła
class ResetPasswordRequestAPIView(APIView):
    permission_classes = [~IsAuthenticated]

    def post(self,request):
        serializer=ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result=serializer.save()
        return Response({'result':result}, status=status.HTTP_200_OK)

#widok służący do resetowania hasła
class ResetPasswordAPIView(APIView):
    permission_classes = [~IsAuthenticated]

    def post(self,request):
        serializer=ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result=serializer.save()
        return Response({'result':result}, status=status.HTTP_200_OK)


#Jest to widok służący do utworzenia konta użytkownika oraz ich wylistowania. Zakres użytkowników oraz uprawnienia różnią się w zależności od roli użytkownika
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method.lower()=='get':
            self.permission_classes=[IsAuthenticated]
        elif self.request.method.lower()=='post':
            self.permission_classes=[IsAdmin]
        elif self.request.method.lower() == 'options':
            self.permission_classes = [DisableOPTIONSMethod]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method.lower()=='get':
            return UserListSerializer
        return UserCreateSerializer

    def get_serializer_context(self):
        context=super().get_serializer_context()
        context['is_superuser']=self.request.user.is_superuser
        return context
#mechanik oraz standard mogą wypisać współpracowników z lokacji, menadżer może wyświetlać standardy, mechaników i menadżerów, admin może wypisywać wszystkich poza superuserem, superuser wszystkich
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method.lower()=='get':
            if self.request.user.role=='standard' or self.request.user.role=='mechanic':
                if UserLocationAssignment.objects.filter(user=self.request.user).exists():
                    return qs.filter(user_location_assignment__location=UserLocationAssignment.objects.get(user=self.request.user).location)
                else:
                    return qs.filter(pk=self.request.user.pk)
            elif self.request.user.role=='manager':
                return qs.exclude(role='admin')
            elif self.request.user.role=='admin' and self.request.user.is_superuser==False:
                return qs.exclude(is_superuser=True)
        return qs

class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method.lower() in ('put','patch','delete'):
            return UserUpdateSerializer
        return UserRetrieveSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.request.method.lower()=='get':
            self.permission_classes=[IsAuthenticated]
        elif self.request.method.lower() in ('put','patch','delete'):
            self.permission_classes=[IsAdminOrSuperuserAndTargetUserHasLowerRole]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method.lower()=='get':
            if self.request.user.role == 'standard' or self.request.user.role == 'mechanic':
                if UserLocationAssignment.objects.filter(user=self.request.user).exists():
                    return qs.filter(user_location_assignment__location=UserLocationAssignment.objects.get(
                        user=self.request.user).location)
                else:
                    return qs.filter(pk=self.request.user.pk)
            elif self.request.user.role == 'manager':
                return qs.exclude(role='admin')
            elif self.request.user.role == 'admin' and self.request.user.is_superuser == False:
                return qs.exclude(is_superuser=True)
        return qs

class AssignUserToLocationAPIView(generics.CreateAPIView):
    queryset = UserLocationAssignment.objects.all()
    serializer_class = UserLocationAssignmentSerializer

    def get_permissions(self):
        if self.request.method.lower()=='post':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

class UnassignUserFromLocationAPIView(APIView):
    def delete(self,request,user_id):
        obj=get_object_or_404(UserLocationAssignment,user_id=user_id)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method.lower()=='delete':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

class FailureReportListCreateAPIView(generics.ListCreateAPIView):
    queryset = FailureReport.objects.all()
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.request.method.lower()=='get':
            return FailureReportListSerializer
        return FailureReportCreateSerializer

    def get_permissions(self):
        if self.request.method.lower()=='post':
            self.permission_classes=[IsStandard]
        elif self.request.method.lower()=='get':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

class FailureReportRetrieveAPIView(generics.RetrieveAPIView):
    queryset = FailureReport.objects.all()
    serializer_class = FailureReportRetrieveSerializer
    def get_permissions(self):
        if self.request.method.lower()=='get':
            self.permission_classes=[IsManager|IsAdmin]
        elif self.request.method.lower()=='options':
            self.permission_classes=[DisableOPTIONSMethod]
        return super().get_permissions()

#TODO wytestować bo syfny kod
class FailureReportAssignWorkshopAPIView(APIView):
    def post(self, request):
        serializer=FailureReportAssignWorkshopSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result=serializer.save()
        return Response({'result':result}, status=status.HTTP_200_OK)