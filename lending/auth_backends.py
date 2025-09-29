# lending/auth_backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from lending.models import MemberProfile

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    """Authenticate using email OR phone number and password."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None

        # Try email first
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Try phone number from MemberProfile
            try:
                profile = MemberProfile.objects.get(phone_number=username)
                user = profile.user
            except MemberProfile.DoesNotExist:
                return None

        if user and user.check_password(password):
            return user
        return None
