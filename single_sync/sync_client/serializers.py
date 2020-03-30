from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.decorators import action

from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = User
        extra_kwargs = {
            'username': {'validators': []},
        }



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
