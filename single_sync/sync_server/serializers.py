from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = User


class PermissionSerializer(serializers.Serializer):
    codename = serializers.CharField(min_length=3, max_length=256, required=True)
    name = serializers.CharField(min_length=3, max_length=256, required=True)
    app_label = serializers.CharField(min_length=3, max_length=256, required=True)
    model = serializers.CharField(min_length=3, max_length=256, required=True)



class SyncServerSerializer(serializers.Serializer):
    client_id = serializers.CharField(min_length=3, max_length=256, required=True)
    token = serializers.CharField(min_length=3, max_length=256, required=True)


class SyncPermissionSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=PermissionSerializer()
    )
