import binascii
import os

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, RequestsClient, APITestCase, APISimpleTestCase

from registration.models import Client
from sbilife import settings


# Create your tests here.
class CreateWorkOrderTestCase(APITestCase):
    def setUp(self) -> None:
        call_command('setup_public')
        defaults = {
            'password': binascii.hexlify(os.urandom(20)).decode()
        }
        user_obj = User.objects.get(email=settings.ADMIN_USER)
        client = Client(user=user_obj, client_id='KWRJSEWQ7P',
                        client_secret='k3px11bghd7w2rbsec8hdnuz1qv01e62h9xrduz4filozd13gpo7q3szc7d4mzg1')
        client.save()

    def test_create_workorder(self):
        # client = APIClient()
        headers = {
            'client-id': '`KWRJSEWQ7P`',
            'client-secret': 'k3px11bghd7w2rbsec8hdnuz1qv01e62h9xrduz4filozd13gpo7q3szc7d4mzg1',
            'Content-Type': 'application/json'
        }
        self.client.login(**headers)
        resp = self.client.post(reverse('claim_application:api.create_work_order'), data={
            "data": "Ki-DJnq-xC2SO_H6rodbfTRqzDOWudvz4IcZImuYovPkjsqqnkjKktH3wZGVu5WV1UK0xTdNUx3baeJQdN5kmnFQfvBRSkgM709ytgvpjSdr4Lx51GxXcJX8KNgAMniOpA5Rx4Mnqg5T9D2mmD1U_SsSvFr-V1YN1KuDsxtShZA6Pxf_JULbj52HkxCvSyJoKJtprWhXp_8PpugsKdHRbdwE-75BiCbAiK1Rm94Vde5c9JleFb-bhCqhiFkCy1GGcCRpvsa1PRLx12eNz9P8fCs3vw71gF3DV5ksU5U1Jfb8Kcn-dImgWseS0nf1OIYmj2YUkJ3vk6foBjctPHiNRJajY5UcjPRw5CCrKJsS2ZjDl_-86DrP5TKrFgLLZCjC8H2OanjJjN-hRD9lVH2AjDtLBoNuQWeGBPflFFnfKvNt0_n_mkcEMfLVvz-Xz48H7Nok1pPMN72JO1Uc1ygGiwwN1VtyMTeUu58gQ-2eYc4ijv-5NRJPE3fIhdfY7Ks29GzT3-ueK6r2eQRuID6qMaz56TKz2cCkrLnya_h3ceV60yvMIJ5feGGKD8e_cBDZXffL5jNCZGA-JgOIW7xKw9DpxlEWyXR8eADR5BgcFk7GB1mruQ0uqkV8FBy-HDMDQ6bJFTr3JjkfGvRU8wJZfKzlKCfPr54wyDTasydnHLf3BQKMNVEiTAn9PyQYZxv_BRjPd9yqOb0MR5Q2PYraCxZ8bA38kbAb3XSpPX2B2ebL3_i3QfPRA_rRbQxlndXw4LvXd1iqCUC6EAezQ3YLHYY8UfXwKe4BS_-aafyerpVZEAMhpAiD37FRkSJXYMZ6Ypp7RtWPOltJMqQtmyJjKpOWuKP1dEBs2JlsLOy5lBKHUEwGh3wJ1Reo6VRJRw6XpqyoNRdC9vr6S3b-znlDXiURpgWu8wNfGeftELZDhATHIi8Ehch5aR9TznMYs8sgxO-N0739XwWOah6yKIy-z29IP69XzS7m-cdZJwXDphoddXlc0fUpwzX1FJTeUAJQcX43n0Ob3HvcHnU-_uAp7gTgvuyuGE9eNXNSb2aD_N421UTUVQqv-0m_JWbULNRjKr8TBCBnsDuoAW6h0fsY44WPDWNJibUj0erjXbLwU_dy_kp_nDIgFa5yNFar2uyu5IP-ydJJGU8NQzlcE5B0K7wn2BrrQz8dJtyJMOuTi4NYz6g406Ss7_KW0j2TC_fdzB2wgHhVQZrSqKR568k7m3UsHW7OXxcUS8kLWhPFMwx27UJuYeRr7oqmma-ulo6e98oOBmBdKhLuJWGGcoBGqHLw0eDvzuGC8X6Lp9_6pJoGeKYlyxiQV3SSuNwBl9sBdf9x3qzpsY0K-0Q9Gx9FvMt5Eg3j0DjA2jrpj0fD_ZDWRaArp_qJmW9dQ3JHP5qcfqKIxgcMTe7n6jfnggpCgJavyQQSQUHGYMDGAH4RpFpy_-bv4LT-T7IDN43KoKt2bKO7j-Z5M569Iem9DeZwmTqduiXSr_g3McdGMdAf7LRLtjNxJtMiQAtLnMjczYs2wH1siBmuf0lS_uqE3OETMmX0GpF1dVjU_wy6O72MlsHLi0oKqeysm_qSYA0IkolKiXJKrwv8_5boXRR9hTFvd4dA3wY4or45158OYxUPj3gnmUWvMvRnAyaj4XuBRGSwufHsLTnfiLPHzn-SkCMFkun2Aq7iZG1RX0jCnPhJNaq_camQEhGvYqhMrjKqCf84okoIhm3aEg_U28USZFwg4iSDz8x-BZubxOaicNfAgvODyAQ6nVjjZlF9E5V-rtb3b5cZVNB5aP3lbHwUaNF2sHXWEQ_X_nfXZ8735oDhuGPQyPMEQbtOmiuRv2KAB46nWExxfJEAJ8sqsqIoM_OrMuE_FhV0p37x8zHA5M2oH9iSuu6G9uzpX00m5YZo1zsqQ2Yh1uObwy9jc1J3lglJPV4RGtaJa9iWhRaxqh-XGzo="
        }, headers=headers)
