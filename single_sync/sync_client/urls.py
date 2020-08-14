from django.urls import path
from .views import default_test_view, sync_client_test_view,regenerate_permissions

urlpatterns = [
    path('default-test-view/',default_test_view),
    path('sync-client-view/',sync_client_test_view),
    path('regenerate-permissions/',regenerate_permissions),
]
