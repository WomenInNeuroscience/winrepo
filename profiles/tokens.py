import jwt
import datetime
from django.utils import timezone
from django.conf import settings


class Token:

    audience = ""
    expires_in = 60 * 60 * 24 * 7

    @classmethod
    def generate(cls, **payload):
        return jwt.encode(
            {
                **payload,
                "aud": cls.audience,
                "exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(seconds=cls.expires_in)
            },
            settings.SECRET_KEY,
            algorithm='HS256',
        )

    @classmethod
    def check(cls, token, **extra):
        try:
            return jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256'],
                audience=cls.audience,
                **extra
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class UserCreateToken(Token):

    audience = "user_create"
    expires_in = 60 * 10

    @classmethod
    def generate(cls, user, **extra):
        return super().generate(
            **extra,
            sub=user.id,
        )


class UserPasswordResetToken(Token):

    audience = "user_password_reset"
    expires_in = 60 * 10

    @classmethod
    def generate(cls, user, **extra):
        return super().generate(
            **extra,
            sub=user.id,
        )

