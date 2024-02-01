import io
import uuid

import pandas as pd
from django.core.files.base import ContentFile
from django.core.management import BaseCommand
from django.db import transaction

from claim_application.models import TempDumpFilesLog
from claim_application.utils import change_timezone_for_dataframe
from master.models import ExtractionConfiguration, DigitalMasterField, MasterType
from master.models import MasterField
from master.models import MasterPageLabel


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        print("SETTING UP...")
        message = ''
        temp_dump = TempDumpFilesLog.objects.create(status=TempDumpFilesLog.PROCESSING)
        try:
            ec = ExtractionConfiguration.objects.all()
            ec_df = pd.DataFrame.from_records(
                ec.values('id', 'process_url',
                          'page_classification_url', 'extra_params'))

            mt = MasterType.objects.all()
            mt_df = pd.DataFrame.from_records(mt.values())
            change_timezone_for_dataframe(mt_df)

            mpl = MasterPageLabel.objects.all()
            mpl_df = pd.DataFrame.from_records(
                mpl.values('id', 'configuration', 'type__code', 'name', 'code', 'tag_name', 'default', 'is_active'))

            mf = MasterField.objects.all()
            mf_df = pd.DataFrame.from_records(
                mf.values('id', 'data_type', 'configuration', 'page_label__type__tag_name',
                          'page_label__tag_name', 'name',
                          'output_max_length', 'output_decimals_digit',
                          'output_date_formate',
                          'code', 'tag_name',
                          'ml_model_name',
                          'do_postprocessing',
                          'is_multi_line', 'is_active', ))

            dmf = DigitalMasterField.objects.all()
            dmf_df = pd.DataFrame.from_records(dmf.values())
            change_timezone_for_dataframe(dmf_df)
            with io.BytesIO() as buffer:
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    ec_df.to_excel(writer, sheet_name='ExtractionConfiguration')
                    mt_df.to_excel(writer, sheet_name='MasterType')
                    mpl_df.to_excel(writer, sheet_name='MasterPageLabel')
                    mf_df.to_excel(writer, sheet_name='MasterField')
                    dmf_df.to_excel(writer, sheet_name='DigitalMasterField')
                excel_content = buffer.getvalue()
            temp_dump.file.save('export_data_{}.xlsx'.format({uuid.uuid4().hex[0:7]}), ContentFile(excel_content),
                                save=True)
            message = 'Export data Completed.'
            temp_dump.status = TempDumpFilesLog.COMPLETED
        except Exception as e:
            message = str(e)
            temp_dump.status = TempDumpFilesLog.ERROR
        temp_dump.message = message
        temp_dump.save()

        print(message)
        print("SETUP COMPLETE.")
