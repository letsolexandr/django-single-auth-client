from django.db import models


class AppRegister(models.Model):
    client_id = models.CharField(max_length=256, unique=True)
    secret = models.CharField(max_length=256, unique=True)
    last_token_check = models.DateTimeField(auto_now=True, null=True)
    first_token_check = models.DateTimeField(null=True)
    client_host = models.CharField(max_length=256, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
