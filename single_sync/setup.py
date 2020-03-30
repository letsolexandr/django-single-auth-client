import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='single_sync',
    version='0.1',
    packages=['sync_server','sync_client'],
    description='A line of description',
    long_description=README,
    author='Olexandr Lets',
    author_email='letsolexandr@gmail.com',
    url='https://github.com/yourname/django-myapp/',
    license='MIT',
    install_requires=[
        'Django>2.1,<2.2',
        'djangorestframework',
        'markdown',
        'django-filter',
        'drf-yasg-edge'
    ]
)