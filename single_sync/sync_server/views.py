from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.views import APIView
from .server import ServerSync
from .serializers import  SyncServerSerializer,SyncPermissionSerializer

class SyncEndPoint(APIView):
    """Return all user info by token, info was encrypted by client secret key"""
    def post(self, request: Request):
        req_serializer = SyncServerSerializer(data=request.data)
        if req_serializer.is_valid():
            ss = ServerSync()
            info = ss.get_all_info(req_serializer.validated_data)
            return Response(info)
        else:
            return Response(req_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class SyncPermissions(APIView):
    ""
    def post(self, request: Request):
        req_serializer = SyncPermissionSerializer(data=request.data)
        if req_serializer.is_valid():
            data = req_serializer.validated_data
            ss = ServerSync()
            info = ss.sync_permissions(data.get('permissions'))
            return Response(info)
        else:
            return Response(req_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


