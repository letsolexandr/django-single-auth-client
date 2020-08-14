from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = User


class PermissionSerializer(serializers.Serializer):
    codename = serializers.CharField( max_length=256, required=True)
    name = serializers.CharField(max_length=256, required=True)
    app_label = serializers.CharField( max_length=256, required=True)
    model = serializers.CharField(max_length=256, required=True)



class SyncServerSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=256, required=True)
    token = serializers.CharField(max_length=256, required=True)


class SyncPermissionSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=PermissionSerializer()
    )
