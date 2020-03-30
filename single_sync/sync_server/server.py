from typing import Dict

from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer


class ServerSync():

    def get_all_info(self, data: Dict) -> Dict:
        """ Check token and return all user info if token exist"""
        ### {'token_exist':True, 'user':{user_data},'user_permissions_all':[{'id':1,'codename':'n',}]}
        token = data.get('token')
        if self.validate_token(token):
            res = {'token_exist': True}
            res.update(self.get_user_info(token))
            return res
        else:
            return {'token_exist': False}

    def validate_token(self, token) -> bool:
        """Check if token exist in db"""
        try:
            Token.objects.get(key=token)
            return True
        except models.ObjectDoesNotExist:
            return False

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
            perm['app_label']=perm['content_type__app_label']
            perm['model']=perm['content_type__model']
            del perm['content_type__app_label']
            del perm['content_type__model']
            format_perm = f"{perm.get('app_label')}.{perm.get('codename')}"
            if format_perm in user_permission_list:
                user_permissions.append(perm)

        res = dict(
            user_data=UserSerializer(user).data,
            user_permissions_all=user_permissions)
        return res

    def sync_permissions(self, permissions):
        ###Check content types, create if not exist
        q_ct = [perm for perm in permissions if perm.get('app_label') not in permissions]
        exist_ct = list(ContentType.objects.filter(app_label__in=q_ct).values_list('app_label', flat=True))
        non_exist_ct = [perm for perm in permissions if perm.get('app_label') not in exist_ct]
        for ct in non_exist_ct:
            if not ContentType.objects.filter(app_label=ct.get('app_label'),
                                              model=ct.get('model')).exists():
                new_ct = ContentType()
                new_ct.app_label = ct.get('app_label')
                new_ct.model = ct.get('model')
                new_ct.save()
            ##ct.update({'content_type':new_ct})
        ###Check permissions, create if not exist
        all_perm = list(Permission.objects.all().values_list('codename', flat=True))
        q_perm = [perm for perm in permissions if perm.get('codename') not in all_perm]
        updated_values = 0
        for perm in q_perm:
            ct = ContentType.objects.get(model=perm.get('model'),
                                         app_label=perm.get('app_label'))
            perm.update({'content_type': ct})
            del perm['app_label']
            del perm['model']
            Permission.objects.create(**perm)
            updated_values += 1
        return {'updated_values': updated_values}
