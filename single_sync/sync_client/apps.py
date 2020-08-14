from django.apps import AppConfig
from django.db.models.signals import post_migrate


def migration_callback(sender, **kwargs):
    from .processing import sync_permissions
    sync_permissions()


class AuthSyncClientConfig(AppConfig):
    name = 'sync_client'

    def ready(self):
        post_migrate.connect(migration_callback, sender=self)
