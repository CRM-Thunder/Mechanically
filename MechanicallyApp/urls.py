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
    path('users/activate/', views.AccountActivationAPIView.as_view(), name='user-activation'),
    path('users/reset-password/', views.ResetPasswordAPIView.as_view(), name='user-reset-password'),
    path('users/reset-password-request/', views.ResetPasswordRequestAPIView.as_view(), name='user-reset-password-request'),
    path('users/', views.UserListCreateAPIView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', views.UserRetrieveUpdateDestroyAPIView.as_view(), name='user-detail'),
    path('users/assign/',views.AssignUserToLocationAPIView.as_view(), name='user-assign'),
    path('users/unassign/<uuid:user_id>/',views.UnassignUserFromLocationAPIView.as_view(), name='user-unassign'),
    path('failure-reports/',views.FailureReportListCreateAPIView.as_view(), name='failure-report-list'),
    path('failure-reports/<uuid:pk>/',views.FailureReportRetrieveAPIView.as_view(), name='failure-report-detail'),
    path('failure-reports/assign/',views.FailureReportAssignPIView.as_view(), name='failure-report-assign'),
    path('failure-reports/dismiss/',views.FailureReportDismissedAPIView.as_view(), name='failure-report-dismiss'),
    path('repair-reports/',views.RepairReportListAPIView.as_view(), name='repair-report-list'),
    path('repair-reports/<uuid:pk>/',views.RepairReportRetrieveUpdateAPIView.as_view(), name='repair-report-detail'),
    path('repair-reports/my-workshop',views.CurrentRepairReportsInWorkshopListAPIView.as_view(), name='current-repair-report-list'),
]