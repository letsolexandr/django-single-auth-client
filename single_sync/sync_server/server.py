from typing import Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import signing
from django.db import models
from rest_framework.authtoken.models import Token

from .models import AppRegister
from .serializers import UserSerializer
from utility import timeit

User = get_user_model()


class NonExistClientID(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'Client not exist, client_id ="{0}".client_id ="{0}" not exist on remote server'.format(self.message)
        else:
            return 'Client not exist'


class ClientNotActive(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ClientNotActive. client_id "{0}" not active. Check it on your sync server.'.format(self.message)
        else:
            return 'ClientNotActive'


class TokenNotExist(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'Token not exist. Token "{0}" not exist on remote server'.format(self.message)
        else:
            return 'Token not exist'


class ServerSync():
    @timeit
    def get_all_info(self, data: Dict, request) -> Dict:
        """ Check token and return all user info if token exist"""
        ### {'token_exist':True, 'user':{user_data},'user_permissions_all':[{'id':1,'codename':'n',}]}
        token = data.get('token')
        client_id = data.get('client_id')

        if client_id:
            if not AppRegister.objects.filter(client_id=client_id).exists():
                raise NonExistClientID(client_id)
            else:
                app = AppRegister.objects.get(client_id=client_id)
                if not app.active:
                    raise ClientNotActive(client_id)

        if self.validate_token(token):
            res = {'token_exist': True}
            app: AppRegister = AppRegister.objects.get(client_id=client_id)
            app.client_host = request.META['HTTP_HOST']
            app.save()
            res.update(self.get_user_info(token))
            return res
        else:
            raise TokenNotExist(token)

    @timeit
    def validate_token(self, token) -> bool:
        """Check if token exist in db"""
        try:
            Token.objects.get(key=token)
            return True
        except models.ObjectDoesNotExist:
            return False

    @timeit
    def encrypt_data(self, data, client_id):
        if AppRegister.objects.filter(client_id=client_id).exists():
            key = AppRegister.objects.get(client_id=client_id).secret
            return signing.dumps(data, key=key)
        else:
            raise NonExistClientID

    @timeit
    def decrypt_data(self, data, client_id):
        if AppRegister.objects.filter(client_id=client_id).exists():
            key = AppRegister.objects.get(client_id=client_id).secret
            return signing.loads(data, key=key)
        else:
            raise NonExistClientID

    @timeit
    def get_user_info(self, token: str) -> Dict:
        """ return all user info, user filtered by token"""
        user_token: Token = Token.objects.get(key=token)
        user: User = user_token.user
        user_permissions = []
        user_permission_list = list(user.get_all_permissions())
        permissions = Permission.objects.all()
        permissions = permissions.values('codename', 'name', 'content_type__app_label', 'content_type__model')
        all_perm = list(permissions)
        for perm in all_perm:
            perm['app_label'] = perm['content_type__app_label']
            perm['model'] = perm['content_type__model']
            del perm['content_type__app_label']
            del perm['content_type__model']
            format_perm = f"{perm.get('app_label')}.{perm.get('codename')}"
            if format_perm in user_permission_list:
                user_permissions.append(perm)

        user_data = dict(UserSerializer(instance=user).data)
        user_data['user_permissions'] = user_permission_list
        ##raise Exception(user_permission_list)
        # print('user_data',user_data)
        res = dict(user_data=user_data,
                   user_permissions_all=user_permissions)
        return res

    @timeit
    def sync_permissions(self, permissions):
        ###Check content types, create if not exist
        updated_values = 0
        for perm in permissions:
            ct, created = ContentType.objects.get_or_create(model=perm.get('model'),
                                                            app_label=perm.get('app_label'),
                                                            )
            if not Permission.objects.filter(content_type=ct,
                                             codename=perm.get('codename')).exists():
                Permission.objects.create(name=perm.get('name'),
                                          content_type=ct,
                                          codename=perm.get('codename'),
                                          )
            updated_values += 1
        return {'updated_values': updated_values}
