from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Manufacturer, Location, UserLocationAssignment, Vehicle, User, FailureReport, RepairReport
from .serializers import ManufacturerSerializer, LocationCreateRetrieveSerializer, \
    UserNestedLocationAssignmentSerializer, \
    VehicleCreateUpdateSerializer, VehicleRetrieveSerializer, VehicleListSerializer, AccountActivationSerializer, \
    UserCreateSerializer, UserListSerializer, UserUpdateSerializer, ResetPasswordSerializer, \
    ResetPasswordRequestSerializer, \
    UserRetrieveSerializer, UserLocationAssignmentSerializer, FailureReportCreateSerializer, \
    FailureReportListSerializer, \
    FailureReportRetrieveSerializer, FailureReportAssignSerializer, FailureReportDismissedSerializer, \
    FailureReportReassignSerializer, \
    RepairReportRetrieveUpdateSerializer, RepairReportListSerializer, LocationUpdateSerializer, LocationListSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from .permissions import IsManager, IsAdmin, IsMechanic, DisableUnwantedHTTPMethods, \
    IsAdminOrSuperuserAndTargetUserHasLowerRole, IsStandardAssignedToBranch, IsMechanicAssignedToWorkshop
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.db.models import Q


#TODO: rozważyć usunięcie endpointa my-location i zmodyfikować LocationListSerializer i LocationRetrieveSerializer aby standard i mechanik mogli wyświetlić tylko swoją lokację
UNWANTED_HTTP_METHODS= ('options', 'trace', 'connect')
#dodawać i edytować Manufacturera może administrator, reszta może wypisywać
class ManufacturerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

    def get_permissions(self):
        if self.request.method.lower() == 'post':
            self.permission_classes = [IsAdmin]
        elif self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


class ManufacturerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() in ('put', 'patch', 'delete'):
            self.permission_classes = [IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


#dodawać, usuwać oraz modyfikować lokalizacje może administrator
#wypisywać wszystkie lokalizacje może menadżer i admin
class LocationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    def get_serializer_class(self):
        if self.request.method.lower()=='post':
            return LocationCreateRetrieveSerializer
        return LocationListSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() == 'post':
            self.permission_classes = [IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


class LocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() in ('put','patch','delete'):
            return LocationUpdateSerializer
        return LocationCreateRetrieveSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() in ('put', 'patch', 'delete'):
            self.permission_classes = [IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


#informacje o swojej lokalizacji może wypisywać standard i mechanik
class UserLocationListAPIView(generics.ListAPIView):
    queryset = UserLocationAssignment.objects.all()
    serializer_class = UserNestedLocationAssignmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsMechanicAssignedToWorkshop | IsStandardAssignedToBranch]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


#ten widok umożliwia wypisywanie i tworzenie pojazdów przez menadżera oraz administratora
#za pomocą odpowiednich query setów muszę zaimplementować wypisywanie pojazdów z siedziby standarda
#a także wypisywanie pojazdów przez mechanika, dla których istnieje powiązanie FailureReport z jego warsztatem
class VehicleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleListSerializer

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return VehicleCreateUpdateSerializer
        return VehicleListSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsStandardAssignedToBranch | IsMechanicAssignedToWorkshop| IsManager | IsAdmin]
        elif self.request.method.lower() == 'post':
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()
#TODO: przetestować to z mechanikiem, możliwe błędy semantyczne
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'standard':
            standard_location = UserLocationAssignment.objects.get(user=self.request.user).location
            return qs.filter(location=standard_location)
        elif self.request.user.role == 'mechanic':
            mechanic_location = UserLocationAssignment.objects.get(user=self.request.user).location
            return qs.filter(failure_reports__workshop=mechanic_location)
        return qs


#ten widok umożliwia menadżerowi oraz administratorowi odczytywanie, aktualizowanie oraz usuwanie pojazdu
class VehicleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return VehicleRetrieveSerializer
        return VehicleCreateUpdateSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsStandardAssignedToBranch | IsMechanicAssignedToWorkshop| IsManager | IsAdmin]
        elif self.request.method.lower() in ('put', 'patch', 'delete'):
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()
#TODO: przerzucić na uprawnienia?
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'standard':
            standard_location = UserLocationAssignment.objects.get(user=self.request.user).location
            return qs.filter(location=standard_location)
        elif self.request.user.role == 'mechanic':
            mechanic_location = UserLocationAssignment.objects.get(user=self.request.user).location
            return qs.filter(failure_reports__workshop=mechanic_location)
        return qs


#jest to widok służący do aktywacji konta oraz zmiany hasła z domyślnego na wybrane przez usera
#TODO: przetestować poprawność działania
class AccountActivationAPIView(APIView):
    def get_permissions(self):
        if self.request.method.lower()=='post':
            self.permission_classes = [~IsAuthenticated]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def post(self, request):
        serializer = AccountActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'result': result}, status=status.HTTP_200_OK)


#TODO: przetestować workflow resetu hasła, w przyszłości dodać throttling aby uniknąć DoS
#widok służący do wysyłania email w związku z żądaniem resetu hasła
class ResetPasswordRequestAPIView(APIView):
    def get_permissions(self):
        if self.request.method.lower()=='post':
            self.permission_classes = [~IsAuthenticated]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'result': result}, status=status.HTTP_200_OK)


#widok służący do resetowania hasła
class ResetPasswordAPIView(APIView):
    def get_permissions(self):
        if self.request.method.lower()=='post':
            self.permission_classes = [~IsAuthenticated]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'result': result}, status=status.HTTP_200_OK)


#Jest to widok służący do utworzenia konta użytkownika oraz ich wylistowania. Zakres użytkowników oraz uprawnienia różnią się w zależności od roli użytkownika
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() == 'post':
            self.permission_classes = [IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return UserListSerializer
        return UserCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['is_superuser'] = self.request.user.is_superuser
        return context

    #mechanik oraz standard mogą wypisać współpracowników z lokacji, menadżer może wyświetlać standardy, mechaników i menadżerów, admin może wypisywać wszystkich poza superuserem, superuser wszystkich
    def get_queryset(self):
        qs = super().get_queryset()
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


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method.lower() in ('put', 'patch', 'delete'):
            return UserUpdateSerializer
        return UserRetrieveSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() in ('put', 'patch', 'delete'):
            self.permission_classes = [IsAdminOrSuperuserAndTargetUserHasLowerRole]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
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
        if self.request.method.lower() == 'post':
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


class UnassignUserFromLocationAPIView(APIView):
    def post(self, request, user_id):
        try:
            user=User.objects.get(pk=user_id,role__in=('standard','mechanic'))
        except User.DoesNotExist:
            return Response({'result':'There is no standard user or mechanic user with provided ID.'},status=status.HTTP_404_NOT_FOUND)
        try:
            obj=UserLocationAssignment.objects.get(user_id=user_id)
        except UserLocationAssignment.DoesNotExist:
            return Response({'result':'User is not assigned to any location.'},status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response({'result':'User has been unassigned successfully.'},status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.request.method.lower() == 'post':
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


#TODO: wytestować wszystkie widoki FailureReport
#widok ten służy do tworzenia failure reportów przez standardowego użytkownika oraz wypisywania ich przez menadżera i admina
class FailureReportListCreateAPIView(generics.ListCreateAPIView):
    queryset = FailureReport.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return FailureReportListSerializer
        return FailureReportCreateSerializer

    def get_permissions(self):
        if self.request.method.lower() == 'post':
            self.permission_classes = [IsStandardAssignedToBranch]
        elif self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


#to widok dla menadżerów i adminów do wyświetlania dokładnych informacji o danym FailureReport
class FailureReportRetrieveAPIView(generics.RetrieveAPIView):
    queryset = FailureReport.objects.all()
    serializer_class = FailureReportRetrieveSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()


#to widok do pierwszego przypisania warsztatu do failure, tylko dla zgłoszeń w statusie PENDING
class FailureReportAssignPIView(APIView):
    def get_permissions(self):
        if self.request.method.lower() == 'post':
            self.permission_classes = [IsManager]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def post(self, request):
        serializer = FailureReportAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'result': result}, status=status.HTTP_200_OK)


#to widok służący do zamykania sprawy FailureReport poprzez ustawienie statusu DISMISSED
class FailureReportDismissedAPIView(APIView):
    def get_permissions(self):
        if self.request.method.lower() == 'post':
            self.permission_classes = [IsManager]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def post(self, request):
        serializer = FailureReportDismissedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'result': result}, status=status.HTTP_200_OK)

#ten widok służy do ponownego przypisania już wcześniej przypisanego failure reportu do warsztatu w przypadku gdy warsztat został usunięty lub menadżer postanowi go zmienić
class FailureReportReassignAPIView(APIView):
    def get_permissions(self):
        if self.request.method.lower() == 'post':
            self.permission_classes = [IsManager]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def post(self, request):
        serializer = FailureReportReassignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'result': result}, status=status.HTTP_200_OK)


#widok do wypisywania wszystkich repair reportów/do filtrowania, tylko dla menadżera i admina
class RepairReportListAPIView(generics.ListAPIView):
    queryset = RepairReport.objects.all()
    serializer_class = RepairReportListSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsManager | IsAdmin]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

#TODO:dokładnie wytestować poprawność wylistowanych repair reportów
#widok ten służy do wyświetlenia wszystkich failure + repair przypisanych do warsztatu, w którym pracuje mechanik
class CurrentRepairReportsInWorkshopListAPIView(generics.ListAPIView):
    serializer_class = RepairReportListSerializer
    permission_classes = [IsMechanicAssignedToWorkshop]

    def get_queryset(self):
        mechanic_workshop = get_object_or_404(UserLocationAssignment, user=self.request.user).location
        return RepairReport.objects.filter(failure_report__workshop=mechanic_workshop)

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsMechanicAssignedToWorkshop]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

#TODO:dokładnie wytestować poprawność wylistowanych repair reportów
#widok ten służy do wypisania wszystkich historycznych failure + repair dla pojazdu o zadanym id. Pojazd ten musi być przypisany do naprawy do danego warsztatu, w którym pracuje mechanik
class RelatedVehicleRepairReportsListAPIView(APIView):
    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsMechanicAssignedToWorkshop]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()

    def get(self,request,vehicle_id):
        mechanic_workshop = get_object_or_404(UserLocationAssignment, user=self.request.user).location
        if RepairReport.objects.filter(failure_report__vehicle_id=vehicle_id, failure_report__workshop=mechanic_workshop, status__in=['A', 'R']).exists():
            repair_reports = RepairReport.objects.filter(failure_report__vehicle_id=vehicle_id, status='H')
            serializer = RepairReportListSerializer(repair_reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise NotFound("There is no vehicle with provided id assigned to repair in your workshop.")

#TODO: dokładnie wytestować wybór queryseta
class RepairReportRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = RepairReport.objects.all()
    serializer_class = RepairReportRetrieveUpdateSerializer
#TODO:przerzucić odpowiedzialność na klasy uprawnień? Object permissions będą sprawdzane przy retrieve/put w przeciwieństwie do listowania powyżej
    def get_queryset(self):
        qs=super().get_queryset()
        if self.request.user.role == 'mechanic':
            mechanic_workshop = get_object_or_404(UserLocationAssignment, user=self.request.user).location
            if self.request.method.lower() in ('get','head'):
                pk=self.kwargs.get('pk')
                vehicle_id=RepairReport.objects.get(pk=pk).failure_report.vehicle.id
                if RepairReport.objects.filter(failure_report__vehicle_id=vehicle_id, failure_report__workshop=mechanic_workshop, status__in=['A', 'R']).exists():
                    return qs.filter(Q(failure_report__workshop=mechanic_workshop) | Q(failure_report__vehicle_id=vehicle_id, status='H'))
                else:
                    return qs.filter(failure_report__workshop=mechanic_workshop)
            elif self.request.method.lower() in ('put', 'patch'):
                return qs.filter(failure_report__workshop=mechanic_workshop, status__in=['A', 'R'])
        return qs

    # TODO: stworzyć nowy rodzaj uprawnień dla mechanika przypisanego do danego warsztatu
    def get_permissions(self):
        if self.request.method.lower() in ('put', 'patch'):
            self.permission_classes = [IsMechanic]
        elif self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsManager | IsAdmin | IsMechanic]
        elif self.request.method.lower() in UNWANTED_HTTP_METHODS:
            self.permission_classes = [DisableUnwantedHTTPMethods]
        return super().get_permissions()
