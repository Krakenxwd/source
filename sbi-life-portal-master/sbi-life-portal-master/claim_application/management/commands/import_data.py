import io

import numpy as np
import pandas as pd
from django.core.management import BaseCommand
from django.db import IntegrityError

from claim_application.models import TempDumpFilesLog
from master.models import ExtractionConfiguration, DigitalMasterField, MasterType
from master.models import MasterField
from master.models import MasterPageLabel


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-id', '--temp_id', type=str,
                            dest='temp_id', help='Temporary Id')

    def handle(self, *args, **options):
        message = ''
        temp_id = options['temp_id']
        temp_dump = TempDumpFilesLog.objects.create(status=TempDumpFilesLog.PROCESSING)
        print("SETTING UP...")
        try:
            print('**** Start Importing Data ****')
            temp_obj = TempDumpFilesLog.objects.get(id=temp_id)
            io_obj = io.BytesIO(temp_obj.file.read())
            df = pd.read_excel(io_obj, sheet_name='ExtractionConfiguration')
            df = df.replace({np.nan: None})
            for index, row in df.iterrows():
                try:
                    ExtractionConfiguration.objects.update_or_create(process_url=row['process_url'],
                                                                     page_classification_url=row[
                                                                         "page_classification_url"],
                                                                     extra_params=row['extra_params'])
                except IntegrityError as e:
                    temp_dump.status = TempDumpFilesLog.ERROR
                    message += " {}".format(str(e))
                    print('extraction configuration already exists.')

            ec = ExtractionConfiguration.objects.first()
            df = pd.read_excel(io_obj, sheet_name='MasterType')
            df = df.replace({np.nan: None})

            for index, row in df.iterrows():
                try:
                    MasterType.objects.get_or_create(configuration=ec,
                                                     name=row["name"],
                                                     code=row["code"],
                                                     tag_name=row["tag_name"],
                                                     is_active=row["is_active"])
                except IntegrityError as e:
                    temp_dump.status = TempDumpFilesLog.ERROR
                    message += " {}".format(str(e))
                    print(f'{row["name"]} master type already exists with {row["code"]} code name.')

            df = pd.read_excel(io_obj, sheet_name='MasterPageLabel')
            df = df.replace({np.nan: None})

            for index, row in df.iterrows():
                master_type = MasterType.objects.filter(code=row['type__code']).first()
                try:
                    MasterPageLabel.objects.get_or_create(configuration=ec,
                                                          type=master_type,
                                                          name=row["name"],
                                                          code=row["code"],
                                                          tag_name=row["tag_name"],
                                                          default=row["default"],
                                                          is_active=row["is_active"])
                except IntegrityError as e:
                    temp_dump.status = TempDumpFilesLog.ERROR
                    message += " {}".format(str(e))
                    print(f'{row["name"]} master page label already exists with {row["code"]} code name.')

            df = pd.read_excel(io_obj, sheet_name='MasterField')
            df = df.replace({np.nan: None})

            for index, row in df.iterrows():
                page_label = MasterPageLabel.objects.filter(
                    tag_name=row["page_label__tag_name"], type__tag_name=row["page_label__type__tag_name"]).first()
                try:
                    MasterField.objects.get_or_create(configuration=ec,
                                                      data_type=row["data_type"],
                                                      page_label=page_label,
                                                      name=row["name"],
                                                      code=row["code"],
                                                      output_date_formate=row['output_date_formate'],
                                                      output_max_length=row['output_max_length'],
                                                      output_decimals_digit=row['output_decimals_digit'],
                                                      tag_name=row["tag_name"],
                                                      ml_model_name=row['ml_model_name'] if row[
                                                          'ml_model_name'] else "",
                                                      do_postprocessing=row["do_postprocessing"],
                                                      is_multi_line=row["is_multi_line"],
                                                      is_active=row["is_active"])
                except IntegrityError:
                    temp_dump.status = TempDumpFilesLog.ERROR
                    message += " {}".format(str(e))
                    print(f'{row["name"]} master field  already exists with {row["code"]} code name.')

            df = pd.read_excel(io_obj, sheet_name='DigitalMasterField')
            df = df.replace({np.nan: None})

            for index, row in df.iterrows():
                try:
                    defaults = {'configuration': ec, 'data_type': row["data_type"], 'name': row["name"],
                                'tag_name': row["tag_name"], 'is_active': row["is_active"],
                                'field_type_name': row["field_type_name"],
                                'header': row["header"], 'output_date_formate': row['output_date_formate'],
                                'output_max_length': row['output_max_length'],
                                'output_decimals_digit': row['output_decimals_digit'],
                                'description': row["description"], 'weightage': row["weightage"],
                                'allow_weightage': row["allow_weightage"], 'expected_score': row["expected_score"],
                                'do_scoring': row["do_scoring"], 'show_annotation': row["show_annotation"],
                                '_order': row["_order"]}
                    DigitalMasterField.objects.get_or_create(code=row["code"], defaults=defaults)
                except IntegrityError:
                    temp_dump.status = TempDumpFilesLog.ERROR
                    message += " {}".format(str(e))
                    print(f'{row["name"]} digital master field  already exists with {row["code"]} code name.')

            message = "Import data SETUP COMPLETE."
            temp_dump.status = TempDumpFilesLog.COMPLETED
        except Exception as e:
            message = str(e)
            temp_dump.status = TempDumpFilesLog.ERROR

        temp_dump.message = message
        temp_dump.save()
        print(message)
