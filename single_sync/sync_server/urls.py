from django.urls import path
from .views import SyncEndPoint,SyncPermissions

urlpatterns = [
    path('sync-endpoint/',SyncEndPoint.as_view() ),
    path('sync-permissions/',SyncPermissions.as_view() ),
]
