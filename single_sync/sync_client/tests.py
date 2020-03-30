from django.test import TestCase
from collections import OrderedDict

from single_sync.sync_client.client import Client


class SimpleTestCreateUser(TestCase):
    def setUp(self):
        print('------------------------------------------------------')
        print(f'-------------{self.__class__.__name__}---------------')
        self.test_token = 'test_token'
        self.client = Client(server_url = 'http://127.0.0.1:8000/sync-server/sync-endpoint/',secret='secret')


    def test_1_token(self):
        self.client.validate_token(self.test_token)
        print('Token:', self.test_token)
        print('Token valid:',self.client.token_valid)
        self.client.load_data(self.test_token)
        print(self.client.data.keys())
        self.assertNotEquals(self.client.data, OrderedDict())
        self.client.check_token()
        self.client.check_user_permission()
        self.client.check_user()
        print('----------------------------')

class SimpleTestExistUser(SimpleTestCreateUser):
    def setUp(self):
        from django.contrib.auth.models import User
        from datetime import datetime
        user_data = {'password': 'pbkdf2_sha256$150000$ym9WKqLQN5nP$nPB5z4+Pl6mq6kGX307UDtV+65RvcGOWj+0qnIcGAjc=',
                     'is_superuser': True,
                     'username': 'root',
                     'first_name': '',
                     'last_name': '',
                     'email': '',
                     'is_staff': True,
                     'is_active': True,
                     'date_joined': datetime(2020, 3, 26, 13, 8, 16, 667836)}

        test_user = User(**user_data)
        test_user.save()
        super(SimpleTestExistUser, self).setUp()