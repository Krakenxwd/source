from django.core.management import BaseCommand
import datetime
from django.db import transaction

from claim_application.models import ApplicationDocument

class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        try:
            print("--------- ADDING INTIMATION DATE ---------")   
            for doc in ApplicationDocument.objects.all():
                if doc.date_of_intimation is None and doc.digital_json_data:
                    formatted_date = datetime.datetime.strptime(doc.digital_json_data.get('date_of_intimation'), '%d/%m/%Y').date()
                    doc.date_of_intimation = formatted_date
                    doc.save()
            print("--------- COMPLETE ADDING INTIMATION DATE ---------")
        except Exception as e:
            print(e)