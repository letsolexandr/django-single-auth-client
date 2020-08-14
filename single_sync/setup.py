import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='single_sync',
    version='0.1.57',
    packages=find_packages(),
    description='Django-rest SSO. Client an Server',
    long_description=README,
    ##include_package_data=True,
    author='Olexandr Lets',
    author_email='letsolexandr@gmail.com',
    url='https://github.com/letsolexandr/django-single-auth-client/tree/7a08839a89c2d5ed587cbdcb6232ebfdf586e9a4/single_sync',
    license='MIT',
    install_requires=['requests'],
    python_requires=">=3.6",
    include_package_data=True
)
