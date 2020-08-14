from requests import post

from django.contrib.auth.models import Permission
from django.conf import settings

from .utils import encrypt_data

def sync_permissions():
    permissions = Permission.objects.all()
    permissions = permissions.values('codename', 'name', 'content_type__app_label', 'content_type__model')
    all_perm = list(permissions)
    formated_perm_list = []
    for perm in all_perm:
        perm['app_label'] = perm['content_type__app_label']
        perm['model'] = perm['content_type__model']
        del perm['content_type__app_label']
        del perm['content_type__model']
        ##perm['codename'] = f"{perm.get('app_label')}.{perm.get('codename')}"
        formated_perm_list.append(perm)

    data = {'client_id': settings.AUTH_SERVER_CLIENT_ID, 'permissions': encrypt_data(formated_perm_list)}
    print('-' * 50 + '\n')

    response = post(settings.AUTH_SERVER_SYNC_PERMISSION_URL, data)

    if response.status_code == 200:
        print(response.json())
    else:
        raise Exception(response.text)