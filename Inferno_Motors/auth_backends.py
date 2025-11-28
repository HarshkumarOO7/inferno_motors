# Inferno_Motors/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)
UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Authenticate with email (case-insensitive). Returns user if password matches.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Accept either email kwarg or username param (common call patterns)
        email = kwargs.get('email') or username
        if not email or not password:
            logger.debug("EmailBackend: missing email or password")
            return None

        # normalize/strip spaces
        email = email.strip().lower()

        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            logger.debug("EmailBackend: no user with email %s", email)
            return None

        # check active state first (ModelBackend.user_can_authenticate)
        if not self.user_can_authenticate(user):
            logger.debug("EmailBackend: user cannot authenticate (is_active=%s) for %s", getattr(user, "is_active", None), email)
            return None

        # final password check
        if user.check_password(password):
            logger.debug("EmailBackend: password OK for %s", email)
            return user

        logger.debug("EmailBackend: password FAILED for %s", email)
        return None
