import base64
import datetime
import json
import random
import string
from collections import OrderedDict

import requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView

from base.error_messages import MESSAGE
from rest_framework import exceptions


class CustomGenericAPIView(GenericAPIView):
    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated(custom_response(False, message=MESSAGE['NotAuthenticated']))
        raise exceptions.PermissionDenied(detail=MESSAGE['PermissionDenied'], code=code)


class BearerAuth(TokenAuthentication):
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(custom_response(False, message=MESSAGE['Unauthenticated']))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(custom_response(False, message=MESSAGE['user_not']))

        return super(BearerAuth, self).authenticate_credentials(key)


def code_decoder(data=None, encoded=None, timestamp=None):
    if encoded:
        return base64.b64decode(encoded).decode('utf-8')
    else:
        encode = "Unired".encode('utf-8') + data.encode('utf-8') + "Mobile".encode('utf-8') \
                 + str(datetime.datetime.now().timestamp()).encode()
        return base64.b64encode(encode).decode()


# def code_decoder(data=None):
#
#     key = Fernet.generate_key()
#     f = Fernet(key)
#     return f.encrypt(data.encode('utf-8')).decode()


def sms_sender(url, token, phone, code, lang='ru'):
    temp = {
        'ru': f"Kode: {code}\n\nUnired Mobile\nVnimaniye! Ne soobshyayte etot kod postoronnim.(Sotrudniki UNIRED "
              f"NIKOGDA ne "
              "zaprashivayut kod) Etim mogut vospolzovatsya moshenniki!",
        'en': f"Code: {code}\n\nUnired Mobile\nAttention! Do not share this code with others.(UNIRED employees NEVER "
              f"ask for a "
              "code) Scammers can take advantage of this!",
        'uz': f"Kod: {code}\n\nUnired Mobile\nOgoh bo'ling! Ushbu parolni hech kimga bermang.(UNIRED xodimlari uni "
              f"HECH QACHON "
              "so'ramaydi) Firibgarlar foydalanishiga yo'l qo'ymang! ",
    }
    payload = json.dumps({
        "method": "send",
        "params": [
            {
                "phone": phone,
                "content": temp[lang]
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.post(url, headers=headers, data=payload).status_code
    return response


def otp_sms_sender(url, token, phone, code, amount, card_mask, lang='uz'):
    temp = {
        'ru': f"Unired Mobile\n\nС вашей карты {card_mask} списывается сумма в размере {amount} Введите проверочный код."
              f"Koд: {code}",
        'en': f"Unired Mobile\n\n{amount} will be debited from your {card_mask} card. Enter the code"
              f"\nCode: {code}",
        'uz': f"Unired Mobile\n\nSizning {card_mask} kartangizdan {amount} miqdorida pul yechilmoqda tasdiqlash "
              f"kodini kiriting. "
              f"\nKod: {code}",
    }
    payload = json.dumps({
        "method": "send",
        "params": [
            {
                "phone": phone,
                "content": temp[lang]
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.post(url, headers=headers, data=payload)
    return response.status_code


def format_access(data):
    return OrderedDict([
        ('id', data.id),
        ('uuid', data.uuid),
        ('reg_id', data.reg_id),
        ('last_ip', data.last_ip),
        ('device_name', data.device_name),
        ('version', data.version),
        ('is_primary', data.is_primary),
        ('last_action_time', data.last_action_time),
    ])


def success_response(data=None):
    return OrderedDict([
        ("data", data)
    ])


def error_response(data=None):
    return OrderedDict([
        ("message", data)
    ])


def custom_response(status, data=None, message=None):
    if data is None:
        data = []
    if status:
        return OrderedDict([
            ('status', status),
            ('data', data)
        ])
    else:
        return OrderedDict([
            ('status', status),
            ('message', message)
        ])


def generate_otp(_length=5):
    return ''.join(random.SystemRandom().choice(string.digits) for _ in range(_length))
