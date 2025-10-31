from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import Manufacturer, Location, UserLocationAssignment, Vehicle, User, FailureReport, RepairReport, \
    RepairReportRejection, City
from .serializers import ManufacturerSerializer, LocationCreateSerializer, \
    UserNestedLocationAssignmentSerializer, \
    VehicleCreateUpdateSerializer, VehicleRetrieveSerializer, VehicleListSerializer, AccountActivationSerializer, \
    UserCreateSerializer, UserListSerializer, UserUpdateSerializer, ResetPasswordSerializer, \
    ResetPasswordRequestSerializer, \
    UserRetrieveSerializer, UserLocationAssignmentSerializer, FailureReportCreateSerializer, \
    FailureReportListSerializer, \
    FailureReportRetrieveSerializer, FailureReportAssignSerializer, \
    FailureReportReassignSerializer, \
    RepairReportRetrieveUpdateSerializer, RepairReportListSerializer, LocationUpdateSerializer, LocationListSerializer, \
    RepairReportRejectionSerializer, RepairReportRejectionListSerializer, RepairReportRejectionRetrieveSerializer, \
    PasswordChangeSerializer, LoginSerializer, CitySerializer, LocationRetrieveSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from .permissions import IsManager, IsAdmin, \
    IsAdminOrSuperuserAndTargetUserHasLowerRole, IsStandardAssignedToBranch, IsMechanicAssignedToWorkshop, \
    IsManagerThatManagesSelectedFailureReport, IsAccountOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from django.db.models import Q
from django_filters import rest_framework as external_filters
from .filters import LocationFilter, VehicleFilter, UserFilter, FailureReportFilter, RepairReportFilter, \
    RepairReportRejectionFilter


#dodawać i edytować Manufacturera może administrator, reszta może wypisywać

class UserLoginAPIView(APIView):
    permission_classes = [~IsAuthenticated]
    http_method_names = ['post']
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'
    def post(self, request):
        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        if username is None or password is None:
            raise ValidationError({'detail':'Credentials were not provided.'})
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail':'Username or password is incorrect.'})
        user=authenticate(request, username=username, password=password)
        if user is None:
            raise ValidationError({'detail':'Username or password is incorrect.'})
        login(request, user)
        return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)

class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)

class ManufacturerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    http_method_names = ['head', 'get', 'post']
    filter_backends = (external_filters.DjangoFilterBackend,)
    def get_permissions(self):
        if self.request.method.lower() == 'post':
            self.permission_classes = [IsAdmin]
        elif self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class CityListCreateAPIView(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    http_method_names = ['head', 'get', 'post']
    filter_backends = (external_filters.DjangoFilterBackend,)
    permission_classes = [IsAdmin]

class CityRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    http_method_names = ['head', 'get', 'put', 'patch', 'delete']
    permission_classes = [IsAdmin]

class ManufacturerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    http_method_names = ['head', 'get', 'put', 'patch', 'delete']
    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() in ('put', 'patch', 'delete'):
            self.permission_classes = [IsAdmin]
        return super().get_permissions()


#dodawać, usuwać oraz modyfikować lokalizacje może administrator
#wypisywać wszystkie lokalizacje mogą wszyscy
class LocationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    http_method_names = ['head', 'get', 'post']
    filter_backends = (external_filters.DjangoFilterBackend,)
    filterset_class = LocationFilter
    def get_serializer_class(self):
        if self.request.method.lower()=='post':
            return LocationCreateSerializer
        return LocationListSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() == 'post':
            self.permission_classes = [IsAdmin]
        return super().get_permissions()


class LocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    http_method_names = ['head', 'get', 'put', 'patch', 'delete']
    def get_serializer_class(self):
        if self.request.method.lower() in ('put','patch','delete'):
            return LocationUpdateSerializer
        return LocationRetrieveSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() in ('put', 'patch', 'delete'):
            self.permission_classes = [IsAdmin]
        return super().get_permissions()


#informacje o swojej lokalizacji może wypisywać standard i mechanik
class UserLocationAPIView(APIView):
    permission_classes = [IsMechanicAssignedToWorkshop | IsStandardAssignedToBranch]
    http_method_names = ['head', 'get']

    def get(self, request):
        user_location_assignment = UserLocationAssignment.objects.filter(user_id=request.user.id).first()
        if user_location_assignment is None:
            raise NotFound('Your account is not assigned to any location.')
        else:
            serializer=UserNestedLocationAssignmentSerializer(user_location_assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)

#ten widok umożliwia wypisywanie i tworzenie pojazdów przez menadżera oraz administratora
#za pomocą odpowiednich query setów muszę zaimplementować wypisywanie pojazdów z siedziby standarda
#a także wypisywanie pojazdów przez mechanika, dla których istnieje powiązanie FailureReport z jego warsztatem
class VehicleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleListSerializer
    http_method_names = ['head', 'get', 'post']
    filter_backends = (external_filters.DjangoFilterBackend,)
    filterset_class = VehicleFilter
    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return VehicleCreateUpdateSerializer
        return VehicleListSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsStandardAssignedToBranch | IsMechanicAssignedToWorkshop| IsManager | IsAdmin]
        elif self.request.method.lower() == 'post':
            self.permission_classes = [IsManager | IsAdmin]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role in ('standard', 'mechanic'):
            location_id = UserLocationAssignment.objects.filter(user_id=self.request.user.id).values_list('location_id', flat=True).first()
            if location_id is not None:
                if self.request.user.role == 'standard':
                    return qs.filter(location_id=location_id)
                elif self.request.user.role == 'mechanic':
                    return qs.filter(failure_reports__workshop_id=location_id)
        elif self.request.user.role in ('manager', 'admin'):
            return qs
        return qs.none()


#ten widok umożliwia menadżerowi oraz administratorowi odczytywanie, aktualizowanie oraz usuwanie pojazdu
class VehicleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    http_method_names = ['head', 'get', 'put', 'patch', 'delete']
    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return VehicleRetrieveSerializer
        return VehicleCreateUpdateSerializer

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsStandardAssignedToBranch | IsMechanicAssignedToWorkshop| IsManager | IsAdmin]
        elif self.request.method.lower() in ('put', 'patch', 'delete'):
            self.permission_classes = [IsManager | IsAdmin]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role in ('standard','mechanic'):
            location_id=UserLocationAssignment.objects.filter(user_id=self.request.user.id).values_list('location_id',flat=True).first()
            if location_id is not None:
                if self.request.user.role == 'standard':
                    return qs.filter(location_id=location_id)
                elif self.request.user.role == 'mechanic':
                    return qs.filter(failure_reports__workshop_id=location_id)
        elif self.request.user.role in ('manager', 'admin'):
            return qs
        return qs.none()


#jest to widok służący do aktywacji konta oraz zmiany hasła z domyślnego na wybrane przez usera
class AccountActivationAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [~IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope='account_activation'

    def post(self, request):
        serializer = AccountActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'message': result}, status=status.HTTP_200_OK)

#widok służący do wysyłania email w związku z żądaniem resetu hasła
class ResetPasswordRequestAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [~IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset_request'
    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'message': result}, status=status.HTTP_200_OK)


#widok służący do resetowania hasła
class ResetPasswordAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [~IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'message': result}, status=status.HTTP_200_OK)

#widok służący do zmiany hasła przez zalogowanego użytkownika
class PasswordChangeAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [IsAccountOwner]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_change'
    def post(self, request):
        user = User.objects.filter(pk=self.request.user.pk).first()
        if user is None:
            raise NotFound('There is no user with provided ID.')
        self.check_object_permissions(self.request, user)
        serializer=PasswordChangeSerializer(data=request.data, context={'user': self.request.user})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({'message': result}, status=status.HTTP_200_OK)


#Jest to widok służący do utworzenia konta użytkownika oraz ich wylistowania. Zakres użytkowników oraz uprawnienia różnią się w zależności od roli użytkownika
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    http_method_names = ['head', 'get', 'post']
    filter_backends = (external_filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() == 'post':
            self.permission_classes = [IsAdmin]
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
            user_location_id=UserLocationAssignment.objects.filter(user=self.request.user).values_list('location_id',flat=True).first()
            if user_location_id is not None:
                return qs.filter(user_location_assignment__location_id=user_location_id)
            else:
                return qs.filter(pk=self.request.user.pk)
        elif self.request.user.role == 'manager':
            return qs.exclude(role='admin')
        elif self.request.user.role == 'admin' and self.request.user.is_superuser == False:
            return qs.exclude(is_superuser=True)
        elif self.request.user.role == 'admin' and self.request.user.is_superuser == True:
            return qs
        return qs.none()

class UserProfileAPIView(APIView):
    permission_classes = [IsAccountOwner]
    http_method_names = ['head', 'get']

    def get(self, request):
        user=User.objects.filter(pk=self.request.user.pk).first()
        if user is None:
            raise NotFound('There is no user with provided ID.')
        self.check_object_permissions(self.request, user)
        serializer=UserRetrieveSerializer(user, context={'request': request, 'user_profile_endpoint':True})
        return Response(serializer.data,status=status.HTTP_200_OK)

class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    http_method_names = ['head', 'get', 'put', 'patch', 'delete']
    def get_serializer_class(self):
        if self.request.method.lower() in ('put', 'patch', 'delete'):
            return UserUpdateSerializer
        return UserRetrieveSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['user_profile_endpoint']=False
        return context

    def get_permissions(self):
        if self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsAuthenticated]
        elif self.request.method.lower() in ('put', 'patch', 'delete'):
            self.permission_classes = [IsAdminOrSuperuserAndTargetUserHasLowerRole]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'standard' or self.request.user.role == 'mechanic':
            user_location_id = UserLocationAssignment.objects.filter(user_id=self.request.user.id).values_list('location_id',flat=True).first()
            if user_location_id is not None:
                return qs.filter(user_location_assignment__location_id=user_location_id)
            else:
                return qs.filter(pk=self.request.user.pk)
        elif self.request.user.role == 'manager':
            return qs.exclude(role='admin')
        elif self.request.user.role == 'admin' and self.request.user.is_superuser == False:
            return qs.exclude(is_superuser=True)
        elif self.request.user.role == 'admin' and self.request.user.is_superuser == True:
            return qs
        return qs.none()

class UserChangeStatusAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [IsAdminOrSuperuserAndTargetUserHasLowerRole]

    def post(self, request, pk):
        if self.request.user.is_superuser:
            user = User.objects.filter(pk=pk).first()
        else:
            user = User.objects.filter(pk=pk).exclude(is_superuser=True).first()
        if user is None:
            raise NotFound('There is no user with provided ID.')
        self.check_object_permissions(self.request, user)
        req_status = request.data.get('status')
        if req_status == 'active':
            if user.is_active:
                raise ValidationError({'detail':'User is already active.'})
            if user.is_new_account:
                raise ValidationError({'detail':'This account is yet to be activated by account owner.'})
            user.is_active = True
            user.save()
            return Response({'message': 'User has been activated.'}, status=status.HTTP_200_OK)
        elif req_status == 'inactive':
            if not user.is_active:
                raise ValidationError({'detail':'User is already inactive.'})
            user.is_active = False
            user.save()
            return Response({'message': 'User has been deactivated.'}, status=status.HTTP_200_OK)
        else:
            raise ValidationError({'status':'Only available status types are: active, inactive.'})



class UserAssignmentAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [IsManager | IsAdmin]

    def post(self,request,pk):
        user = User.objects.filter(pk=pk, role__in=('standard', 'mechanic')).first()
        if user is None:
            raise NotFound('There is no standard user or mechanic user with provided ID.')
        action=request.data.get('action')
        if action == 'assign':
            if UserLocationAssignment.objects.filter(user_id=pk).exists():
                raise ValidationError({'detail':'This user is already assigned to a location.'})
            serializer = UserLocationAssignmentSerializer(data=request.data, context={'user': user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'User has been assigned to location.'}, status=status.HTTP_200_OK)
        elif action == 'unassign':
            obj = UserLocationAssignment.objects.filter(user_id=pk).first()
            if obj is None:
                raise ValidationError({'detail':'User is not assigned to any location.'})
            obj.delete()
            return Response({'message': 'User has been unassigned.'}, status=status.HTTP_200_OK)
        else:
            raise ValidationError({'action':'Only available actions are: assign, unassign.'})


#widok ten służy do tworzenia failure reportów przez standardowego użytkownika oraz wypisywania ich przez menadżera i admina
class FailureReportListCreateAPIView(generics.ListCreateAPIView):
    queryset = FailureReport.objects.all()
    http_method_names = ['head', 'get', 'post']
    filter_backends = (external_filters.DjangoFilterBackend,)
    filterset_class = FailureReportFilter
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
        return super().get_permissions()


#to widok dla menadżerów i adminów do wyświetlania dokładnych informacji o danym FailureReport
class FailureReportRetrieveAPIView(generics.RetrieveAPIView):
    queryset = FailureReport.objects.all()
    serializer_class = FailureReportRetrieveSerializer
    http_method_names = ['head', 'get']
    permission_classes = [IsManager | IsAdmin]


class FailureReportActionAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [IsManagerThatManagesSelectedFailureReport]

    def post(self, request, pk):
        failure_report=FailureReport.objects.filter(pk=pk).first()
        if failure_report is None:
            raise NotFound("There is no failure report with provided ID.")

        self.check_object_permissions(self.request, failure_report)
        action=request.data.get('action')

        if action == 'assign':
            if failure_report.status != 'P':
                raise ValidationError({'detail':'Failure report is not in PENDING status.'})

            if failure_report.workshop_id is not None:
                raise ValidationError({'detail':'Failure report has already been assigned to a workshop.'})

            serializer = FailureReportAssignSerializer(data=request.data, context={'failure_report': failure_report})
            serializer.is_valid(raise_exception=True)
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)

        elif action == 'dismiss':
            if failure_report.status != 'P':
                raise ValidationError({'detail':'Failure report is not in PENDING status.'})

            failure_report.status = 'D'
            failure_report.save()
            return Response({'message': 'Failure report has been dismissed.'}, status=status.HTTP_200_OK)

        elif action == 'reassign':
            if failure_report.status not in ('A', 'S'):
                raise ValidationError({'detail':'Failure report is not in ASSIGNED or STOPPED status.'})

            serializer = FailureReportReassignSerializer(data=request.data, context={'failure_report': failure_report})
            serializer.is_valid(raise_exception=True)
            result = serializer.save()
            return Response({'message': result}, status=status.HTTP_200_OK)

        elif action == 'resolve':
            if failure_report.status != 'A':
                raise ValidationError({'detail':'Failure report is not in ASSIGNED status.'})

            repair_report = failure_report.repair_report
            if repair_report.status != 'R':
                raise ValidationError({'detail':'Repair report is not in READY status.'})

            with transaction.atomic():
                vehicle = failure_report.vehicle
                repair_report.status = 'H'
                failure_report.status = 'R'
                vehicle.availability = 'A'
                repair_report.save()
                failure_report.save()
                vehicle.save()
            return Response({'message': 'Failure report has been resolved.'}, status=status.HTTP_200_OK)
        else:
            raise ValidationError({'action':'Only available actions are: assign, reassign, dismiss, resolve'})

#widok do obtainowania i releasowania failure reportu przez managera
class FailureReportManagementAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [IsManagerThatManagesSelectedFailureReport]

    def post(self, request, pk):
        try:
            failure_report=FailureReport.objects.get(pk=pk)
        except FailureReport.DoesNotExist:
            raise NotFound("There is no failure report with provided ID.")

        if failure_report.status not in ('P', 'A', 'S'):
            raise ValidationError({'detail':'Failure report is not in PENDING, ASSIGNED or STOPPED status.'})

        action=request.data.get('action')
        if action == 'obtain':
            if failure_report.managed_by is not None:
                if failure_report.managed_by == self.request.user:
                    raise ValidationError({'detail':'Failure report is already managed by you.'})
                raise ValidationError({'detail':'Failure report is already managed by another manager.'})

            failure_report.managed_by = self.request.user
            failure_report.save()
            return Response({'message': 'Failure report is now managed by your account.'}, status=status.HTTP_200_OK)
        elif action == 'release':
            self.check_object_permissions(self.request, failure_report)
            failure_report.managed_by = None
            failure_report.save()
            return Response({'message': 'Failure report is no longer managed by your account.'},status=status.HTTP_200_OK)
        else:
            raise ValidationError({'action':'Only available actions are: obtain, release.'})

#widok do wypisywania wszystkich repair reportów/do filtrowania, tylko dla menadżera i admina
class RepairReportListAPIView(generics.ListAPIView):
    queryset = RepairReport.objects.all()
    serializer_class = RepairReportListSerializer
    http_method_names = ['head', 'get']
    permission_classes = [IsManager | IsAdmin]
    filter_backends = (external_filters.DjangoFilterBackend,)
    filterset_class = RepairReportFilter
#TODO: ten querysecik do pracy jako przykład
    def get_queryset(self):
        qs=super().get_queryset()
        if self.request.user.role=='manager':
            return qs.filter(failure_report__managed_by_id=self.request.user.id)
        elif self.request.user.role=='admin':
            return qs
        return qs.none()

#widok ten służy do wyświetlenia wszystkich failure + repair przypisanych do warsztatu, w którym pracuje mechanik
class RepairReportsInWorkshopListAPIView(generics.ListAPIView):
    serializer_class = RepairReportListSerializer
    permission_classes = [IsMechanicAssignedToWorkshop]
    http_method_names = ['head', 'get']
    filter_backends = (external_filters.DjangoFilterBackend,)
    filterset_class = RepairReportFilter

    def get_queryset(self):
        mechanic_workshop_id=UserLocationAssignment.objects.filter(user_id=self.request.user.id,location__location_type='W').values_list('location_id',flat=True).first()
        if mechanic_workshop_id is not None:
            return RepairReport.objects.filter(failure_report__workshop_id=mechanic_workshop_id)
        else:
            return RepairReport.objects.none()

#widok ten służy do wypisania wszystkich historycznych failure + repair dla pojazdu o zadanym id. Pojazd ten musi być przypisany do naprawy do danego warsztatu, w którym pracuje mechanik
class RelatedVehicleRepairReportsListAPIView(APIView):
    http_method_names = ['get','head']
    permission_classes = [IsMechanicAssignedToWorkshop]

    def get(self,request,vehicle_id):
        mechanic_workshop_id=UserLocationAssignment.objects.filter(user_id=self.request.user.id, location__location_type='W').values_list('location_id',flat=True).first()
        if mechanic_workshop_id is not None:
            #sprawdzenie czy dla danego pojazdu istnieje failure_report przypisany do warsztatu mechanika o statusie ACTIVE albo READY: oznacza to, że pojazd jest przydzielony do naprawy w warsztacie mechanika
            if RepairReport.objects.filter(failure_report__vehicle_id=vehicle_id, failure_report__workshop_id=mechanic_workshop_id, status__in=['A', 'R']).exists():
                repair_reports = RepairReport.objects.filter(failure_report__vehicle_id=vehicle_id, status='H')
                serializer = RepairReportListSerializer(repair_reports, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                raise NotFound("There is no vehicle with provided id assigned to repair in your workshop.")
        else:
            raise NotFound("You are not assigned to any location.")

class RepairReportRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = RepairReport.objects.all()
    serializer_class = RepairReportRetrieveUpdateSerializer
    http_method_names = ['head', 'get', 'put', 'patch']

    def get_permissions(self):
        if self.request.method.lower() in ('put', 'patch'):
            self.permission_classes = [IsMechanicAssignedToWorkshop]
        elif self.request.method.lower() in ('get','head'):
            self.permission_classes = [IsManager | IsAdmin | IsMechanicAssignedToWorkshop]
        return super().get_permissions()

    def get_queryset(self):
        qs=super().get_queryset()
        if self.request.user.role == 'mechanic':
            mechanic_workshop_id=UserLocationAssignment.objects.filter(user_id=self.request.user.id,location__location_type='W').values_list('location_id',flat=True).first()
            if mechanic_workshop_id is not None:
                if self.request.method.lower() in ('get','head'):
                    pk=self.kwargs.get('pk')
                    vehicle_id=RepairReport.objects.filter(pk=pk).values_list('failure_report__vehicle_id',flat=True).first()
                    if vehicle_id is not None and RepairReport.objects.filter(failure_report__vehicle_id=vehicle_id, failure_report__workshop_id=mechanic_workshop_id, status__in=['A', 'R']).exists():
                        return qs.filter(Q(failure_report__workshop_id=mechanic_workshop_id) | Q(failure_report__vehicle_id=vehicle_id, status='H'))
                    else:
                        return qs.filter(failure_report__workshop_id=mechanic_workshop_id)
                elif self.request.method.lower() in ('put', 'patch'):
                    return qs.filter(failure_report__workshop_id=mechanic_workshop_id)
        elif self.request.user.role=='manager':
            return qs.filter(failure_report__managed_by_id=self.request.user.id)
        elif self.request.user.role=='admin':
            return qs
        return qs.none()

class RepairReportChangeStatusAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [IsMechanicAssignedToWorkshop]
    def post(self, request, pk):
        mechanic_workshop_id=UserLocationAssignment.objects.filter(user_id=self.request.user.id,location__location_type='W').values_list('location_id',flat=True).first()
        if mechanic_workshop_id is None:
            raise NotFound("You are not assigned to any location.")
        repair_report=RepairReport.objects.filter(pk=pk,failure_report__workshop_id=mechanic_workshop_id).first()
        if repair_report is None:
            raise NotFound("There is no repair report with provided ID.")
        req_status=request.data.get('status')
        if req_status=='ready':
            if repair_report.status != 'A':
                raise ValidationError({'detail':'Repair report is not in ACTIVE status.'})
            else:
                repair_report.status = 'R'
                repair_report.save()
                return Response({'message': 'Repair report has been set as ready.'}, status=status.HTTP_200_OK)
        elif req_status=='active':
            if repair_report.status != 'R':
                raise ValidationError({'detail':'Repair report is not in READY status.'})
            else:
                repair_report.status = 'A'
                repair_report.save()
                return Response({'message':'Repair report has been set as active.'}, status=status.HTTP_200_OK)
        else:
            raise ValidationError({'status':'Available status types are: ready, active.'})





class RepairReportRejectAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [IsManager]

    def post(self, request, pk):
        repair_report=RepairReport.objects.filter(pk=pk, failure_report__managed_by_id=self.request.user.id).first()
        if repair_report is None:
            raise NotFound("There is no repair report with provided ID.")
        if repair_report.status != 'R':
            raise ValidationError({'detail':'Repair report is not in READY status.'})

        serializer=RepairReportRejectionSerializer(data=request.data,context={'repair_report':repair_report})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            serializer.save()
            repair_report.status='A'
            repair_report.save()
            return Response({'message': 'Repair report has been rejected.'}, status=status.HTTP_200_OK)


class RepairReportRejectionListAPIView(generics.ListAPIView):
    queryset = RepairReportRejection.objects.all()
    serializer_class = RepairReportRejectionListSerializer
    permission_classes = [IsManager | IsAdmin |IsMechanicAssignedToWorkshop]
    http_method_names = ['head', 'get']
    filter_backends = (external_filters.DjangoFilterBackend,)
    filterset_class = RepairReportRejectionFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs=super().get_queryset()
        if self.request.user.role == 'mechanic':
            mechanic_workshop_id=UserLocationAssignment.objects.filter(user_id=self.request.user.id,location__location_type='W').values_list('location_id',flat=True).first()
            if mechanic_workshop_id is not None:
                return qs.filter(repair_report__failure_report__workshop_id=mechanic_workshop_id)
        elif self.request.user.role=='manager':
            return qs.filter(repair_report__failure_report__managed_by_id=self.request.user.id)
        elif self.request.user.role =='admin':
            return qs
        return qs.none()

class RepairReportRejectionRetrieveAPIView(generics.RetrieveAPIView):
    queryset = RepairReportRejection.objects.all()
    serializer_class = RepairReportRejectionRetrieveSerializer
    permission_classes = [IsManager | IsAdmin | IsMechanicAssignedToWorkshop]
    http_method_names = ['head', 'get']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs=super().get_queryset()
        if self.request.user.role == 'mechanic':
            mechanic_workshop_id=UserLocationAssignment.objects.filter(user_id=self.request.user.id,location__location_type='W').values_list('location_id',flat=True).first()
            if mechanic_workshop_id is not None:
                return qs.filter(repair_report__failure_report__workshop_id=mechanic_workshop_id)

        elif self.request.user.role=='manager':
            return qs.filter(repair_report__failure_report__managed_by_id=self.request.user.id)
        elif self.request.user.role=='admin':
            return qs
        return qs.none()

