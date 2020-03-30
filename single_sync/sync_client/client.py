from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Permission, Group
from collections import OrderedDict
from django.contrib.contenttypes.models import ContentType
##from django.db import models
from requests import post
from typing import List
from django.conf import settings
from .serializers import UserSerializer, SyncServerResultSerializer
from .models import TokenValidation


class Client:
    def __init__(self, server_url: str = None, secret: str = None):
        self.server_url = server_url or settings.AUTH_SERVER_CHECK_TOKEN_URL
        self.secret_ = secret or settings.AUTH_SERVER_SECRET_KEY
        self.token_valid = False
        self.token_exist = True
        self.errors = []
        self.data = OrderedDict()

    def run_validation(self, token):
        self.validate_token(token)
        if self.token_valid:
            return True, self.errors
        else:
            return self.check_all(token), self.errors

    def validate_token(self, token):
        """Check if given token exist in db"""
        if Token.objects.filter(key=token).exists():
            token = Token.objects.get(key=token)
            self.token_validation, created = TokenValidation.objects.get_or_create(token=token)
            if created:
                self.token_valid = True
            else:
                validation_age = self.token_validation.get_age()
                print(f'AGE:{int(validation_age / 60)} minutes')
                if validation_age > settings.AUTH_SERVER_MAX_TOKEN_AGE:
                    self.token_valid = False
                    self.token_validation.set_validation_checkpoint()
                else:
                    self.token_valid = True
        else:
            self.token_valid = False

    def check_all(self, token):
        self.load_data(token)
        self.check_token()
        self.check_user_permission()
        self.check_user()

        return self.token_valid, self.errors

    def load_data(self, token):
        """Load data from auth server"""
        request_data = {'client_id': settings.AUTH_SERVER_CLIENT_ID,
                        'token': token
                        }
        response = post(self.server_url, request_data)

        if response.status_code == 200:
            data = response.json()
            if 'token_exist' in data.keys():
                token_exist = data.get('token_exist')
                if not token_exist:
                    self.errors.append(f'token "{token}" not exist on remote server')
                    self.token_valid = False
                    return
            else:
                self.errors.append('Remote server return not valid result')
                self.token_valid = False
                return

            serializer = SyncServerResultSerializer(data=data)
            if serializer.is_valid():
                # {'token_exist':True, 'user_data':{user_data},'user_permissions_all':[{'id':1,'codename':'n',}]}
                self.data = serializer.validated_data
            elif User.objects.filter(username=data.get('user_data').get('username')).exists():
                user = User.objects.filter(username=data.get('user_data').get('username')).first()
                data['user_data'] = UserSerializer(user).data
                print('User:', user)
                serializer = SyncServerResultSerializer(data=data)
                if serializer.is_valid():
                    self.data = serializer.validated_data
                else:
                    self.errors = self.errors + serializer.errors
                    print('Serializer errors:', serializer.errors)
            else:
                self.data = OrderedDict()
                self.errors = self.errors + serializer.errors
                print('Serializer errors:', serializer.errors)
                print('Response:', response.json())
        elif response.status_code == 400:
            self.errors.append(response.text)
        else:
            self.errors.append(response.text)

    def check_token(self):
        """Check if token exist on remote server"""
        if self.data.get('token_exist'):
            self.token_valid = True
        else:
            self.token_valid = False

    def check_user(self):
        """ Check user, if user is not exist create with the same password and etc"""
        if not self.token_valid:
            return

        if self.data.get('user_data'):
            serialized_user = UserSerializer(data=self.data.get('user_data'))
            if serialized_user.is_valid():
                user_data = serialized_user.validated_data
                self._check_user(user_data)
            else:
                self.errors = self.errors + serialized_user.error_messages
                print('Check user errors', serialized_user.error_messages)
        else:
            raise Exception('User data not exist')

    def _check_user(self, user_data):
        if User.objects.filter(username=user_data.get('username')).exists():
            user = User.objects.filter(username=user_data.get('username')).first()
            user_changed = False
            for key, value in user_data.items():
                if hasattr(user, key) and getattr(user, key) != value:
                    ##update user params if not equal
                    user_changed = True
                    if key in ['groups', 'user_permissions']:
                        groups = set(Group.objects.filter(pk__in=user_data.get('groups')))
                        user_permissions = set(Permission.objects.filter(pk__in=user_data.get('user_permissions')))
                        user.groups.add(*groups)
                        user.user_permissions.add(*user_permissions)
                    else:
                        setattr(user, key, value)

            if user_changed:
                user.save()
            print('User changed:', user)
        else:
            _user_data = dict(user_data).copy()
            groups = set(Group.objects.filter(pk__in=_user_data.pop('groups')))
            user_permissions = set(Permission.objects.filter(pk__in=_user_data.pop('user_permissions')))
            user = User(**_user_data)
            user.save()
            user.groups.add(*groups)
            user.user_permissions.add(*user_permissions)
            print('User created:', user)

    def check_user_permission(self):
        if not self.token_valid:
            return
        user_permissions: List = self.data.get('user_permissions_all')
        for user_permission in user_permissions:
            content_type, created = ContentType.objects.get_or_create(
                app_label=user_permission.get('app_label'), model=user_permission.get('model'),
            )
            ##user_permission = {codename:'',, app_label:'', model:''}
            if not Permission.objects.filter(name=user_permission.get('name'), content_type=content_type,
                                             codename=user_permission.get('codename')).exists():
                perm = Permission()
                perm.name = user_permission.get('name')
                perm.content_type = content_type
                perm.codename = user_permission.get('codename')
                perm.save()
