from typing import List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import signing
from requests import post
from rest_framework.authtoken.models import Token

from .exceptions import ClientException
from .models import TokenValidation
from .serializers import SyncServerResultSerializer
from .utils import convert_to_list, nested_convert_to_dict, encrypt_data, decrypt_data
from utility import timeit

User = get_user_model()


class Client:
    def __init__(self, server_url: str = None, secret: str = None):
        self.server_url = server_url or settings.AUTH_SERVER_CHECK_TOKEN_URL
        self.secret_ = secret or settings.AUTH_SERVER_SECRET_KEY
        self.token_valid = False
        self.token_exist = True
        self.errors = []
        self.data = {}

    @timeit
    def run_validation(self, token):
        self.validate_token(token)
        if self.token_valid:
            return [True, self.errors]
        else:
            return self.check_all(token)

    @timeit
    def validate_token(self, token):
        """Check if given token exist in db"""
        if Token.objects.filter(key=token).exists():
            self.token_validation, created = TokenValidation.objects.get_or_create(token=token)
            self.token_valid = self.token_validation.token_valid
            if not self.token_valid:
                return

            validation_age = self.token_validation.get_age()
            print(f'AGE:{int(validation_age / 60)} minutes')
            if validation_age > settings.AUTH_SERVER_MAX_TOKEN_AGE:
                self.token_validation.set_validation_checkpoint()
                self.token_validation.set_validation_status(False)
                self.token_valid = self.token_validation.token_valid
        else:
            self.token_validation, created = TokenValidation.objects.get_or_create(token=token)
            self.token_validation.set_validation_status(False)
            self.token_valid = self.token_validation.token_valid

    @timeit
    def check_all(self, token):
        self.load_data(token)
        self.check_token()
        self.check_user_permission()
        self.check_user()
        self.create_token(token)
        return self.token_valid, self.errors

    @timeit
    def load_data(self, token):
        """Load data from auth server"""
        request_data = {
            'token': token,
            'client_id': settings.AUTH_SERVER_CLIENT_ID,
        }
        encripted_request_data = {'client_id': settings.AUTH_SERVER_CLIENT_ID,
                                  'data': encrypt_data(request_data)}

        response = post(self.server_url, encripted_request_data)

        if response.status_code == 200:
            _data = response.json()
            data = decrypt_data(_data.get('data'))
            self.handle_user_data(data)

        elif response.status_code == 400:
            self.errors.append(response.text)
            self.token_validation.set_validation_status(False)
        elif response.status_code == 404:
            self.token_validation.set_validation_status(False)
            self.errors.append(
                f"""The remote server has no endpoint '{self.server_url}'. Check the file 'urls.py' on your sync-server""")
        else:
            self.token_valid = False
            self.errors.append(response.text)

    @timeit
    def encrypt_data(self, data):
        return signing.dumps(data, key=settings.AUTH_SERVER_SECRET_KEY)

    @timeit
    def decrypt_data(self, data):
        return signing.loads(data, key=settings.AUTH_SERVER_SECRET_KEY)

    @timeit
    def handle_user_data(self, data):
        serializer = SyncServerResultSerializer(data=data)
        if serializer.is_valid():
            self.data = nested_convert_to_dict(serializer.validated_data)
            self.token_validation.set_validation_status(True)
            self.token_valid = self.token_validation.token_valid
        else:
            self.data = {}
            self.errors = self.errors + convert_to_list(serializer.errors)
            raise ClientException(self.errors)

    @timeit
    def check_token(self):
        """Check if token exist on remote server"""
        if self.data.get('token_exist'):
            self.token_valid = True
        else:
            self.token_valid = False

    @timeit
    def check_user(self):
        """ Check user, if user is not exist create with the same password and etc"""
        if not self.token_valid:
            return

        if not self.data.get('user_data'):
            raise Exception('User data not exist')
        else:
            self._check_user(self.data.get('user_data'))

    @timeit
    def _check_user(self, user_data):
        if User.objects.filter(username=user_data.get('username')).exists():
            user = User.objects.filter(username=user_data.get('username')).first()
            user_changed = False
            update_fields = []
            for key, value in user_data.items():
                if hasattr(user, key) and getattr(user, key) != value:
                    ##update user params if not equal
                    user_changed = True
                    ##Пропускаємо поля які не будемо оновлювати
                    if key in ['groups', 'id', 'last_login']:
                        continue
                    if key == 'user_permissions':
                        user_permissions = self.get_permissions_by_names(user_data.get('user_permissions'), user)
                        ## Видаляємо всі дозволи створені попередньо, щоб записати заново
                        user.user_permissions.clear()
                        try:
                            user.user_permissions.add(*user_permissions)
                        except Exception as e:
                            print(e)

                    else:
                        update_fields.append(key)
                        setattr(user, key, value)

            if user_changed:
                ##print('Update fields:', update_fields)
                user.save(update_fields=update_fields)
                ##print('User changed:', user)
            self.user = user
        else:
            _user_data = nested_convert_to_dict(user_data)
            print(_user_data)
            user_permissions = self.get_permissions_by_names(_user_data.pop('user_permissions'))
            user = User(**_user_data)
            user.save()
            ##user.groups.add(*groups)
            user.user_permissions.add(*user_permissions)
            print('User created:', user)
            self.user = user

    @timeit
    def get_permissions_by_names(self, user_permissions, user=None):
        app_name_list = []
        for perm in user_permissions:
            app_name = perm.split('.')[0]
            if app_name not in app_name_list:
                app_name_list.append(app_name)

        app_id_list = list(ContentType.objects.filter(app_label__in=app_name_list).values_list('id', flat=True))

        codename_list = []
        for perm in user_permissions:
            code = perm.split('.')[-1]
            if code not in codename_list:
                codename_list.append(code)

        # Вибираємо всі дозволи користувача вказані на сервері синхронізації
        all_perms = set(
            Permission.objects.filter(codename__in=codename_list, content_type__id__in=app_id_list).distinct())

        return all_perms

    @timeit
    def check_user_permission(self):
        """ Check all permissions. Permissions are not depend of current user"""
        if not self.token_valid:
            return
        user_permissions: List = self.data.get('user_permissions_all')
        ##print('User permissions: ', user_permissions[0])
        for user_permission in user_permissions:
            content_type, created = ContentType.objects.get_or_create(
                app_label=user_permission.get('app_label'), model=user_permission.get('model'),
            )
            codename = user_permission.get('codename')

            if not Permission.objects.filter(content_type=content_type,
                                             codename=codename).exists():
                perm = Permission()
                perm.name = user_permission.get('name')
                perm.content_type = content_type
                perm.codename = codename
                perm.save()
                print('Content type: ', content_type, 'Created: ', created)

    @timeit
    def create_token(self, token):
        if not self.token_valid:
            return

        if not Token.objects.filter(key=token).exists() and self.user:
            ## delete old token for user
            Token.objects.filter(user=self.user).delete()
            ## create new Token
            Token.objects.create(key=token, user=self.user)
