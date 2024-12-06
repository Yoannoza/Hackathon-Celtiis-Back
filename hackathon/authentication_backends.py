from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Jury
from django.contrib.auth.models import AbstractUser,  Group, Permission, User# Importer le modèle Jury

class NameAuthBackend(BaseBackend):
    """
    Custom authentication backend that uses the 'name' field and password.
    """
    def authenticate(self, request, name=None, password=None, **kwargs):
        try:
            user = Jury.objects.get(name=name)
            if user and check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Jury.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
