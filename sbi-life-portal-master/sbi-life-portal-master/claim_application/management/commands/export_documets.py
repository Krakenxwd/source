import datetime
import io
import uuid

import pandas as pd
from django.core.management import BaseCommand
from django.utils.timezone import make_aware

from claim_application.models import ApplicationDocument, TempDumpFilesLog
from claim_application.utils import get_page_level_document_json_data


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-sd', '--start_date', type=str, dest='start_date',
                            help='Start date format %d/%m/%y ex: 01/11/2000')
        parser.add_argument('-ed', '--end_date', type=str, dest='end_date',
                            help='End date format %d/%m/%y ex: 01/11/2000')

    def handle(self, *args, **options):
        start_date = make_aware(datetime.datetime.strptime(options['start_date'], '%d/%m/%Y %H:%M:%S'))
        end_date = make_aware(datetime.datetime.strptime(options['end_date'], '%d/%m/%Y %H:%M:%S'))
        temp_dump = TempDumpFilesLog.objects.create()
        data = []
        for doc in ApplicationDocument.objects.filter(created_at__range=[start_date, end_date]):
            data += get_page_level_document_json_data(doc.id)

        df = pd.json_normalize(data)
        with io.BytesIO() as output_buffer:
            with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Export Document', index=False)
            temp_dump.file.save('{}_export_document_data_{}.xlsx'.format('sbi', uuid.uuid4().hex[0:7]), output_buffer,
                                save=True)
