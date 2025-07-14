from django.urls import path
from . import views

urlpatterns = [
    path('manufacturers/',views.manufacturer_list)
]