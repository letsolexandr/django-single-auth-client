# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from sync_client.authentication import SyncClientAuthentication


@api_view(http_method_names=['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def default_test_view(request):
    data = {'check_result': 'default view check sucess!'}
    return Response(data)


@api_view(http_method_names=['GET', 'POST'])
@authentication_classes([SyncClientAuthentication])
@permission_classes([IsAuthenticated])
def sync_client_test_view(request):
    data = {'check_result': 'Sync client view check sucess!'}
    return Response(data)


@api_view(http_method_names=['GET'])
@authentication_classes([SyncClientAuthentication])
@permission_classes([IsAdminUser])
def regenerate_permissions(request):
    from utility.content_types import regenerate_permissions
    regenerate_permissions()
    return Response({'result': 'ok'})
