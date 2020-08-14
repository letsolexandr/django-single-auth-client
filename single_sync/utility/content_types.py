from django.contrib.contenttypes.management import create_contenttypes
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.auth.management import create_permissions

from django.apps import apps

# Add any missing permissions
def regenerate_content_types():
   ContentType.objects.all().delete()
   app_configs = apps.get_app_configs()
   for app_config in app_configs:
      create_contenttypes(app_config)

# Add any missing permissions
def regenerate_permissions():
   Permission.objects.all().delete()
   app_configs = apps.get_app_configs()
   for app_config in app_configs:
      create_permissions(app_config)
