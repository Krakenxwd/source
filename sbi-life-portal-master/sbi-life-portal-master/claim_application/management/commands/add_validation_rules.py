from django.core.management import BaseCommand
from django.db import transaction
from django.db.models.signals import post_save
from claim_application.models import ValidationConfiguration


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        print("--------- ADDING VALIDATION RULES IF NOT ADDED ---------")
        vc = ValidationConfiguration.objects.order_by(
            "-created_at").first()
        if vc:
            post_save.send(ValidationConfiguration, instance=vc, created=False)
        else:
            print("--- creating ValidationConfiguration ---")
            ValidationConfiguration.objects.create(validation_name='base_validations',
                                                   configuration_for=ValidationConfiguration.DOCUMENT)

        print("--------- COMPLETE VALIDATION RULES ADDING ---------")
