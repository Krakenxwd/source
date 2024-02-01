import re
from base64 import urlsafe_b64encode, urlsafe_b64decode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.padding import PKCS7
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.db.models import Q


def is_valid_email(email):
    regex = re.compile(
        r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def get_domain(request=None):
    if request:
        url = 'https://{}'.format(get_current_site(request))
    else:
        url = 'https://{}'.format(Site.objects.first().domain)
    return url


def send_invite_email_with_password(email, password, send_copy=False):
    from_email = 'Team Glib <admin@glib.ai>'
    subject = 'Invitation to access the portal'
    bcc_list = []
    if send_copy:
        bcc_list = [user.email for user in User.objects.filter(Q(groups__name='admin') | Q(is_superuser=True)).filter(
            is_active=True).distinct()]
    to_email_address_list = [email]
    if send_copy:
        to_email_address_list.append(from_email)
    body = 'Dear {user},\n\n' \
           'We are pleased to invite you to access our portal. You can now log in to the portal using the following ' \
           'credentials:\n\n' \
           'Email: {email}\n\n' \
           'Password: {password}\n\n' \
           'Please use the following link to access the portal: {link_to_portal}\n\n' \
           'If you have any issues accessing the portal or have any questions, please contact us.\n\n' \
           'We look forward to your participation in our portal.\n\n' \
           'Best,\n' \
           'Team Glib'.format(user=email, email=email,
                              password=password,
                              link_to_portal=get_domain())
    send_mail = mail.EmailMessage(subject=subject,
                                  body=body,
                                  from_email=from_email,
                                  to=to_email_address_list,
                                  bcc=bcc_list)
    send_mail.send()


class AesEncrDecrUtil:
    SECRET_KEY = ""
    SALT_VALUE = ""
    ALGORITHM = 'AES'
    SHA_256 = hashes.SHA256()
    KEY_SIZE = 32  # AES-256
    ITERATIONS = 65536
    IV = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def __init__(self, secret_key, salt_value):
        self.SECRET_KEY = secret_key
        self.SALT_VALUE = salt_value

    @staticmethod
    def encrypt(str_to_encrypt, key, salt_value):
        # Key derivation
        kdf = PBKDF2HMAC(
            algorithm=AesEncrDecrUtil.SHA_256,
            length=AesEncrDecrUtil.KEY_SIZE,
            salt=salt_value.encode(),
            iterations=AesEncrDecrUtil.ITERATIONS,
            backend=default_backend()
        )
        key = kdf.derive(key.encode())

        # Padding
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(str_to_encrypt.encode()) + padder.finalize()

        # Encryption
        cipher = Cipher(algorithms.AES(key), modes.CBC(AesEncrDecrUtil.IV), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return urlsafe_b64encode(ct).decode()

    @staticmethod
    def decrypt(str_to_decrypt, key, salt_value):
        # Key derivation
        kdf = PBKDF2HMAC(
            algorithm=AesEncrDecrUtil.SHA_256,
            length=AesEncrDecrUtil.KEY_SIZE,
            salt=salt_value.encode(),
            iterations=AesEncrDecrUtil.ITERATIONS,
            backend=default_backend()
        )
        key = kdf.derive(key.encode())

        # Decryption
        cipher = Cipher(algorithms.AES(key), modes.CBC(AesEncrDecrUtil.IV), backend=default_backend())
        decryptor = cipher.decryptor()
        ct = urlsafe_b64decode(str_to_decrypt)
        decrypted_padded = decryptor.update(ct) + decryptor.finalize()

        # Unpadding
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        return unpadder.update(decrypted_padded) + unpadder.finalize()
