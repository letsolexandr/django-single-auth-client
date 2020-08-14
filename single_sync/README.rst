single-sync
================================

|build-status-image| |codecov-image| |documentation-status-image| |pypi-version| |py-versions|

Огляд
-----
Пакет для реалізації концепції єдиного входу та синхронізації  користувачів та дозволів між додатками.
Додаток створюється як надбудова над  `Django REST framework <https://www.django-rest-framework.org>`_

Під капотом використовує  ``rest_framework.authentication.TokenAuthentication``.

Пакет включає в себе два компоненти:

sync_server - серверна компонента, використовується для вутентифікації та авторизації користувачів.

sync_client - клієнтська компонента установлюється в додатках, які потрібно підключити.

Залежності
----------

-  Python (3.4, 3.5, 3.6, 3.7, 3.8)
-  Django (1.9, 1.10, 1.11, 2.0, 2.1, 2.2, 3.0)
-  Django REST Framework (3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11)

Примітка: Django 3.0 підпримується з Django REST Framework 3.11.

Швидкий старт
-------------

Установка
~~~~~~~~~

Використовуйте ``pip``:

.. code:: bash

    $ pip install -i https://test.pypi.org/simple/ single-sync

Налаштування клієнта
~~~~~~~~~~~~~~~~~~~~

Додайте  ``'sync_client'`` в  ``INSTALLED_APPS``, та відредагуйте налаштування ``REST_FRAMEWORK``:

.. code:: python

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'rest_framework.authtoken',
        'sync_client',
    ]

    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_FILTER_BACKENDS': (
            'django_filters.rest_framework.DjangoFilterBackend',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'sync_client.authentication.SyncClientAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
    }

    AUTH_SERVER_CHECK_TOKEN_URL = 'http://localhost:8000/sync-server/sync-endpoint/'
    AUTH_SERVER_SYNC_PERMISSION_URL = 'http://localhost:8000/sync-server/sync-permissions/'
    AUTH_SERVER_MAX_TOKEN_AGE = 10 * 60  ##10 хвилин
    AUTH_SERVER_SECRET_KEY = 'test_secret'
    AUTH_SERVER_CLIENT_ID = 'test_client'

Відредагуйте  файл ``urls.py``.

.. code:: python

    from django.urls import path,include

    urlpatterns = [
        path('sync-client/',  include('sync_client.urls')),

    ]

Затосуйте міграції:

.. code:: bash

    $ python manage.py migrate

Налаштування сервера
~~~~~~~~~~~~~~~~~~~~

Додайте  ``'sync_server'`` в ``INSTALLED_APPS``  в файлі ``settings.py``.

.. code:: python

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'rest_framework.authtoken',
        'sync_server',
    ]

Відредагуйте  файл ``urls.py``.

.. code:: python

    from django.contrib import admin
    from django.urls import path,include

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('sync-server/',  include('sync_server.urls')),
    ]

Затосуйте міграції:

.. code:: bash

    $ python manage.py migrate


Використання
~~~~~~~~~~~~

Запустіть тестовий сервер sync_server:

.. code:: bash

    $ python manage.py runserver 127.0.0.1:8000

перевірте чи співпадає AUTH_SERVER_CHECK_TOKEN_URL з хостом сервера,внесіть зміни  якщо потрібно.

Запустіть тестовий сервер sync_client:

.. code:: bash

    $ python manage.py runserver 127.0.1.1:8000

Додайте відповідні хости у виключення в обох додатках:

.. code:: python

    ALLOWED_HOSTS = ['127.0.0.1','127.0.1.1']

або просто пропишіть:

.. code:: python

    ALLOWED_HOSTS = ['*']


Реєстрація нового клієнтського додатку на сервері
-------------------------------------------------

Перейдіть в адмін панель за посиланням http://127.0.0.1:8000/admin/sync_server/appregister/
Зареєструйте новий клієнтський додаток:

Client id == AUTH_SERVER_CLIENT_ID;

Secret == AUTH_SERVER_SECRET_KEY;

Active = True;

Створіть новий токен користувача http://127.0.0.1:8000/admin/authtoken/token/

Перевірка доступності
-------------------------------------------------

.. code:: bash

    curl -X GET http://127.0.1.1:8000/sync-client/sync-client-view/ -H 'Authorization: Token <ваш токен>'

Якщо все правильно налаштовано, Ви отрмаєте повідомлення {"check_result":"Sucess!"}


Як працює ?
-------------------------------------------------

1.Запит від користувача приходить на клієнтський додаток.

2.Клієнтський додаток перевіряє наявність токена в заголовках.

3.Клієнтський додаток перевіряє вілідність токена.

4.Клієнтський додаток перевіряє дату період останньої синхронізаціє з сервером. Якщо період перевишує встановлений в налаштуваннях AUTH_SERVER_MAX_TOKEN_AGE, відбувається синхронізація з сервером.

4.1.Повідомлення  з токеном шифрується з використанням AUTH_SERVER_SECRET_KEY та відправляється на точку синхронізації сервера.AUTH_SERVER_CLIENT_ID  не шифрується.

5. Сервер перевіряє наявність клієнта з вказаним AUTH_SERVER_CLIENT_ID, розшифровує повідомлення.

6. Сервер перевіряє чи активний клієнт.

7. Сервер перевіряє наявність токена на сервері.

7.1 Сервер перевіряє content_type з розшифрованого повідомлення, якщо відсутні створює їх на сервері.

8. Сервер формує повідомлення з даними користувача (дані облікового запису, дозволи користувача).

9. Сервер шифрує повідомлення з використанням AUTH_SERVER_SECRET_KEY, та відправляє їх назад клієнту.

10. Клієнт розшифровує повідомлення

11. Клієнт отримує дані користувача, створює користувача якщо такий відсутній.

12. Клієнт оновлює дозволи користувача з отриманого повідомлення.





.. _tox: http://tox.readthedocs.org/en/latest/

.. |build-status-image| image:: https://secure.travis-ci.org/izimobil/django-rest-framework-datatables.svg?branch=master
   :target: http://travis-ci.org/izimobil/django-rest-framework-datatables?branch=master
   :alt: Travis build

.. |codecov-image| image:: https://codecov.io/gh/izimobil/django-rest-framework-datatables/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/izimobil/django-rest-framework-datatables

.. |pypi-version| image:: https://img.shields.io/pypi/v/djangorestframework-datatables.svg
   :target: https://pypi.python.org/pypi/djangorestframework-datatables
   :alt: Pypi version

.. |documentation-status-image| image:: https://readthedocs.org/projects/django-rest-framework-datatables/badge/?version=latest
   :target: http://django-rest-framework-datatables.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. |py-versions| image:: https://img.shields.io/pypi/pyversions/djangorestframework-datatables.svg
   :target: https://img.shields.io/pypi/pyversions/djangorestframework-datatables.svg
   :alt: Python versions

.. |dj-versions| image:: https://img.shields.io/pypi/djversions/djangorestframework-datatables.svg
   :target: https://img.shields.io/pypi/djversions/djangorestframework-datatables.svg
   :alt: Django versions