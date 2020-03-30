from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.http import HttpResponse
from .views import SyncEndPoint


class SimpleTest(TestCase):
    def setUp(self):
        print('SERVER TEST -----------------------------')
        print('run  ---- setUp')
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.data = {'client_id': 'test_client', 'token': 'test_token'}
        print('test data ', self.data)

    def test_endpoint(self):
        print('run  ---- test_endpoint')
        request = self.factory.post('/sync-server/sync-endpoint', self.data)
        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        request.user = AnonymousUser()
        response = SyncEndPoint.as_view()(request)
        self.response = response
        self.assertEqual(response.status_code, 200)
        print(' -----------------------------SERVER TEST')
