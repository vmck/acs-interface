"""Symetrical cryptografic functions

Using HS256 to encrypt data

Used to validate results received by `/submission/<pk>/done`
"""
import jwt
from django.conf import settings


def encrypt(message):
    return jwt.encode(str(message),
                      settings.SECRET_KEY,
                      algorithms=['HS256'])


def decrypt(message):
    return jwt.decode(str(message),
                      settings.SECRET_KEY,
                      algorithms=['HS256'])
