from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand

from master.constants import GROUPS
from master.models import AccountConfiguration


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        # todo : change it to member
        admin, flag = Group.objects.get_or_create(name='admin')

        admin_password = settings.ADMIN_PASSWORD
        user_list = [settings.ADMIN_USER, settings.SFTP_BOT_EMAIL]
        print(user_list)
        try:
            print("***** Setting up a configurations *****")
            ac, is_created = AccountConfiguration.objects.get_or_create(secret_key='1$CYGNET$1',
                                                                        salt_value='1$CYGNET$1')

            print("***** Setting up a groups *****")
            for group in GROUPS:
                Group.objects.get_or_create(name=group[1])

            for email in user_list:
                user = User.objects.filter(email=email).first()
                if user:
                    if not user.is_superuser:
                        user.is_superuser = True
                        user.save()
                    else:
                        print("super-user available : {}".format(email))
                else:
                    user = User.objects.create_superuser(email, email,
                                                         admin_password)
                    print("new superuser create:", email)

                # default group added
                user.groups.add(admin)

        except Exception as e:
            print("Error: ", str(e))
