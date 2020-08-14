from django.core.signing import BadSignature
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SyncServerSerializer, SyncPermissionSerializer
from .server import ServerSync, NonExistClientID, ClientNotActive, TokenNotExist
from utility import timeit

class SingingMixing():

    def decrypt_input_data(self, _data, client_id) -> ([dict, None], bool, [Response, None]):
        try:
            data = self.ss.decrypt_data(_data, client_id)
            return data, True, None
        except NonExistClientID as e:
            return None, False, Response(str(e), status=status.HTTP_401_UNAUTHORIZED)
        except BadSignature as e:
            return None, False, Response(
                [f'client secret  and server secret is not equal. Check "{client_id}" in appRegister',
                 str(e)],
                status=status.HTTP_403_FORBIDDEN)


class SyncEndPoint(SingingMixing, APIView):
    """Return all user info by token, info was encrypted by client secret key"""
    permission_classes = [AllowAny]
    @timeit
    def post(self, request: Request):
        self.ss = ServerSync()
        client_id = request.data.get('client_id')
        _data = request.data.get('data')

        data, valid, exception_responce = self.decrypt_input_data(_data, client_id)
        if not valid:
            return exception_responce
        req_serializer = SyncServerSerializer(data=data)
        if req_serializer.is_valid():
            try:
                info = self.ss.get_all_info(req_serializer.validated_data, request)
                ##print(info)
                info = self.ss.encrypt_data(info, client_id)
                return Response({'data': info})

            except NonExistClientID as e:
                return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)
            except TokenNotExist as e:
                return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)
            except ClientNotActive as e:
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)

        else:
            raise ValidationError(req_serializer.errors)


class SyncPermissions(SingingMixing, APIView):
    ""
    permission_classes = [AllowAny]
    @timeit
    def post(self, request: Request):
        self.ss = ServerSync()
        client_id = request.data.get('client_id')
        _permissions = request.data.get('permissions')

        data, valid, exception_responce = self.decrypt_input_data(_permissions, client_id)
        if not valid:
            return exception_responce
        req_serializer = SyncPermissionSerializer(data={'permissions':data})
        if req_serializer.is_valid():
            data = req_serializer.validated_data
            ##print(data)
            info = self.ss.sync_permissions(data.get('permissions'))
            return Response(info)
        else:
            raise ValidationError(req_serializer.errors)
