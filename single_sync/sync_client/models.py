from django.db import models
from django.utils.timezone import now


class TokenValidation(models.Model):
    token = models.CharField(max_length=256, unique=True)
    last_validation = models.DateTimeField(auto_now_add=True)


    def get_age(self):
        """ return age in seconds"""
        age = int((now() - self.last_validation).seconds)
        return age

    def set_validation_checkpoint(self):
        self.last_validation = now()
        self.save()
