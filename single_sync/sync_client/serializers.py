from rest_framework import serializers

from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    is_staff = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)
    date_joined = serializers.DateTimeField(allow_null=True,required=True)
    password = serializers.CharField(required=True)
    last_login = serializers.DateTimeField(allow_null=True, required=False)
    is_superuser = serializers.BooleanField(required=True)
    user_permissions = serializers.ListField(
        child=serializers.CharField()
    )


class PermissionSerializer(serializers.Serializer):
    codename = serializers.CharField(min_length=3, max_length=256, required=True)
    name = serializers.CharField(min_length=3, max_length=256, required=True)
    app_label = serializers.CharField(min_length=3, max_length=256, required=True)
    model = serializers.CharField(min_length=3, max_length=256, required=True)


class SyncServerResultSerializer(serializers.Serializer):
    token_exist = serializers.BooleanField(required=True)
    user_data = UserSerializer()
    user_permissions_all = serializers.ListField(
        child=PermissionSerializer()
    )
