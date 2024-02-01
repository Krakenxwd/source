import datetime
import io
import json
import os
import uuid
from collections import OrderedDict
from typing import OrderedDict

import PyPDF2
import boto3
import pandas as pd
import pytz
import requests
from PIL import Image
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rapidfuzz import fuzz

from claim_application.constant import DEFAULT_CSV_SEPARATOR
from claim_application.models import ApplicationDocument, ReProcessDocumentEvents, Claimant, ClaimantFields, \
    ExportRefName
from master.models import DigitalMasterField, MasterPageLabel, MasterField, AccountConfiguration
from registration.utils import get_domain


def get_number_of_pages(file, mime_type):
    if 'pdf' in mime_type:
        doc = PyPDF2.PdfFileReader(file.open(), strict=False)
        return doc.numPages
    elif ('tiff' in mime_type) or ('tif' in mime_type):
        image = Image.open(file.open())
        return image.n_frames
    else:
        return 1


def get_number_of_pages_sftp(file, mime_type):
    if 'pdf' in mime_type:
        doc = PyPDF2.PdfFileReader(file, strict=False)
        return doc.numPages
    elif ('tiff' in mime_type) or ('tif' in mime_type):
        image = Image.open(file)
        return image.n_frames
    else:
        return 1


def is_complete_status_or_404(model, *args, **kwargs):
    queryset = model._default_manager.filter(
        Q(status__in=[ApplicationDocument.COMPLETED]))
    return get_object_or_404(queryset, *args, **kwargs)


def get_not_deleted_or_404(model, *args, **kwargs):
    queryset = model._default_manager.filter(~Q(status=ApplicationDocument.DELETED))
    return get_object_or_404(queryset, *args, **kwargs)


def close_rerun_process_events(document_id):
    document = ApplicationDocument.objects.get(id=document_id)
    if document.re_run_events.filter(status=ReProcessDocumentEvents.OPEN).exists():
        document.re_run_events.filter(status=ReProcessDocumentEvents.OPEN).update(
            status=ReProcessDocumentEvents.CLOSE)


def get_file_size(size):
    if size > 1048576:
        return str(round(size / 1048576, 2)) + " MB"
    if size > 1024:
        return str(round(size / 1024, 2)) + " KB"

    return size + " b"


def iobytes_file(path):
    try:
        if path:
            with open(path, 'rb') as f:
                iobytes = io.BytesIO(f.read())
            return iobytes
    except Exception as e:
        print("Error: ", str(e))
    return None


def remove_file_from_dir(path):
    if path and os.path.exists(path):
        os.remove(path)


def download_directory_from_s3(remote_directory_name):
    bucket_name = settings.AWS_S3_BUCKET_NAME
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=remote_directory_name):
        local_path = os.path.join(settings.BASE_DIR, obj.key)
        if not os.path.exists(os.path.dirname(local_path)):
            os.makedirs(os.path.dirname(local_path))
        bucket.download_file(obj.key, local_path)  # save to same path
    return


def download_file_from_s3(path, aws_path):
    if path and aws_path:
        bucket_name = settings.AWS_S3_BUCKET_NAME

        # Create an S3 client
        s3 = boto3.client('s3')

        s3.download_file(
            Filename=path,
            Bucket=bucket_name,
            Key=aws_path
        )
        return path


def upload_file_to_s3(path, object_name=None):
    if path and os.path.exists(path):
        bucket_name = settings.AWS_S3_BUCKET_NAME
        if object_name is None:
            object_name = os.path.relpath(path, settings.MEDIA_ROOT)

        # Create an S3 client
        s3 = boto3.client('s3')

        # Upload the file
        s3.upload_file(path, bucket_name, object_name)

        # file path
        return object_name
    return None


def change_timezone_for_dataframe(df):
    target_timezone = settings.TIME_ZONE
    desired_timezone = target_timezone
    date_format = '%Y-%m-%d %H:%M:%S %Z'

    filtered_keys = [key for key in list(df) if key.endswith('_at')]
    for key in filtered_keys:
        df[key] = pd.to_datetime(df[key])

        # localize tz-naive timestamp if none in all the Series
        if df[key].isna().all():
            df[key] = df[key].dt.tz_localize(desired_timezone)

        df[key] = df[key].dt.tz_convert(desired_timezone)
        df[key] = df[key].dt.strftime(date_format)


def excel_response(df, file_name, sheet_name=None, header=True):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name[:31] if sheet_name else file_name[:31], index=False, header=header)
    writer.close()
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s_%s.xlsx' % (file_name.lower().replace(' ', '_'),
                                                                           uuid.uuid4().hex[0:7])
    return response


def validate_name(text=None, ref_name=None):
    if ref_name is None and text is None:
        return None
    else:
        if ref_name == text:
            return 100
        else:
            average_score = 0
            split_ref_name = ref_name.split(' ')
            split_name = text.split(' ')
            # print(split_ref_name,split_name)
            for idx in range(len(split_ref_name)):
                save_id = None
                max_score = 0.0
                for idy in range(len(split_name)):
                    temp_score = fuzz.QRatio(split_ref_name[idx], split_name[idy])
                    if max_score < temp_score:
                        max_score = temp_score
                        save_id = idy
                if save_id is not None:
                    del split_name[save_id]
                    average_score += max_score
            average_score = average_score / max(len(ref_name.split(' ')), len(text.split(' ')))
            return average_score


def stringify_data(data):
    if isinstance(data, OrderedDict):
        data = dict(data)
        for key, value in data.items():
            data[key] = stringify_data(value)
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = stringify_data(value)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            data[index] = stringify_data(value)
    elif isinstance(data, str):
        return data.strip()
    elif isinstance(data, int) or isinstance(data, float) \
            or isinstance(data, bool):
        return str(data)
    elif isinstance(data, type(None)):
        return ""
    return data


def call_sbilife_authenticate_user(data: dict):
    try:
        url = "https://uat-api.sbilife.co.in/sbilife/uat/NBWorkflowIDP-v1/authenticateUser"
        payload = json.dumps({k: v for k, v in data.items() if k in ['tokenId', 'userId', 'application']})
        headers = {
            'X-IBM-Client-Secret': '41ffd34d9ba78bff832d2bb5212d19a5',
            'X-IBM-Client-Id': '84711c36292a0ee0d9d40b58fe1f5a71',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.status_code
    except Exception as e:
        print("Error: ", str(e))
        return 500


def pandas_title_replacer(df):
    column_name = {}
    for i in df.columns.values:
        export_ref_name = ExportRefName.objects.filter(field_name=i).first()
        if export_ref_name:
            column_name.update({i: export_ref_name.title})
        else:
            column_name.update({i: i})
    df.rename(columns=column_name, inplace=True)
    return df


def get_default_document_data(document_id: ApplicationDocument):
    document = ApplicationDocument.objects.get(id=document_id)
    timezone = pytz.timezone(settings.TIME_ZONE)
    current_site = get_domain()

    # get a name of life assured
    holder_name = ''
    holder = document.claimant_set.filter(type=Claimant.HOLDER).first()
    if holder:
        holder_name_obj = holder.claimant_fields.filter(digital_master_field__code='name',
                                                        digital_master_field__is_active=True).first()
        holder_name = holder_name_obj.value_text if holder_name_obj and holder_name_obj.value_text else ''
    send_object = {
        'ID': str(document.id),
        'Created By': str(document.created_by),
        'Created At': str(datetime.datetime.strftime(document.created_at.astimezone(timezone), '%d-%m-%Y %H:%M:%S %Z%z')),
        'Processed At': str(
            datetime.datetime.strftime(document.job_completed_at.astimezone(timezone), '%d-%m-%Y %H:%M:%S %Z%z')),
        'Process Status': document.status,
        'Num Pages': document.num_pages,
        'Portal Link': "{}{}".format(current_site, document.get_absolute_url()),
        'Reviewed': document.marked_for_reviewed,
        'Document Type': document.master_type.name if document.master_type else '',
        'Policy Number': document.policy_number,
        'Name of Life Insured': holder_name,
        'Date of Intimation': document.date_of_intimation if document.date_of_intimation else '',
    }
    return send_object


def get_claimant_level_data(claimant_id: Claimant):
    claimant = Claimant.objects.get(id=claimant_id)
    claimant_dict = {'customer_id': claimant.customer_id, 'claimant_type': claimant.type}

    for claimant_field in ClaimantFields.objects.filter(
            digital_master_field__is_active=True):
        claimant_dict.update(
            {claimant_field.digital_master_field.header: ''})

    for claimant_field in ClaimantFields.objects.filter(claimant=claimant,
                                                        digital_master_field__is_active=True):
        if claimant_field.digital_master_field.data_type == DigitalMasterField.TEXT:
            if claimant_field.digital_master_field and claimant_field.value_text and len(
                    claimant_field.value_text.strip()) > 0:
                claimant_dict.update(
                    {claimant_field.digital_master_field.header: claimant_field.value_text[
                                                                 :claimant_field.digital_master_field.output_max_length]})
            else:
                claimant_dict.update({claimant_field.digital_master_field.header: claimant_field.value_text})
        elif claimant_field.digital_master_field.data_type == DigitalMasterField.DATE:
            if claimant_field.digital_master_field.output_date_formate and claimant_field.value_date:
                claimant_dict.update(
                    {claimant_field.digital_master_field.header: str(
                        claimant_field.value_date.strftime(
                            claimant_field.digital_master_field.output_date_formate))})
            else:
                claimant_dict.update({claimant_field.digital_master_field.header: str(
                    claimant_field.value_date if claimant_field.value_date else '')})
        elif claimant_field.digital_master_field.data_type == DigitalMasterField.AMOUNT:
            if claimant_field.digital_master_field.output_decimals_digit and claimant_field.value_amount:
                claimant_dict.update({claimant_field.digital_master_field.header: round(
                    claimant_field.value_amount, claimant_field.digital_master_field.output_decimals_digit)})
            else:
                claimant_dict.update({claimant_field.digital_master_field.header: claimant_field.value_amount})
        elif claimant_field.digital_master_field.data_type == DigitalMasterField.BOOLEAN:
            if claimant_field.value_boolean:
                claimant_dict.update({claimant_field.digital_master_field.header: "Yes"})
            else:
                claimant_dict.update({claimant_field.digital_master_field.header: "No"})
    return claimant_dict


def get_page_level_document_json_data(document_id: ApplicationDocument):
    document = ApplicationDocument.objects.get(id=document_id)
    document_dict = get_default_document_data(document.id)
    data = []
    for claimant in Claimant.objects.filter(document=document, type=Claimant.NOMINEE):
        claimant_dict = get_claimant_level_data(claimant.id)

        # Extracted Data Fields
        combined_page_data = OrderedDict()

        for pl in MasterPageLabel.objects.filter(is_active=True):
            for mf in pl.masterfield_set.filter(is_active=True):
                if mf.code in ['full', 'front', 'back', 'face']:
                    continue
                header = f"{' '.join(pl.code.split('_')).title()} {' '.join(mf.code.split('_')).title()}"
                combined_page_data.update({header: ""})

        for page in claimant.get_pages():
            label = page.get_page_label().code
            for i in page.pagefields.filter(is_active=True).order_by('master_field__order'):
                if i.master_field.code in ['full', 'front', 'back', 'face']:
                    continue
                header = f"{' '.join(label.split('_')).title()} {' '.join(i.master_field.code.split('_')).title()}"
                if i.master_field.data_type == MasterField.TEXT:
                    if i.master_field.output_max_length and i.value_text and len(i.value_text.strip()) > 0:
                        combined_page_data.update(
                            {header: i.value_text[:i.master_field.output_max_length]})
                    else:
                        combined_page_data.update({header: i.value_text})
                elif i.master_field.data_type == MasterField.AMOUNT:
                    if i.master_field.output_decimals_digit and i.value_amount:
                        combined_page_data.update({header: round(
                            i.value_amount, i.master_field.output_decimals_digit)})
                    else:
                        combined_page_data.update({header: i.value_amount})
                elif i.master_field.data_type == MasterField.DATE:
                    if i.master_field.output_date_formate and i.value_date:
                        combined_page_data.update(
                            {header: str(i.value_date.strftime(i.master_field.output_date_formate))})
                    else:
                        combined_page_data.update({header: str(i.value_date if i.value_date else '')})
                elif i.master_field.data_type == MasterField.BOOLEAN:
                    if i.value_boolean:
                        combined_page_data.update({header: "Yes"})
                    else:
                        combined_page_data.update({header: "No"})
        data.append({**document_dict, **claimant_dict, **combined_page_data})
    return data


def get_page_level_digital_json_data(document_id: ApplicationDocument):
    data = []
    document = ApplicationDocument.objects.get(id=document_id)
    document_dict = get_default_document_data(document.id)
    for claimant in document.claimant_set.filter(type=Claimant.NOMINEE):
        claimant_dict = get_claimant_level_data(claimant.id)
        data.append({**document_dict, **claimant_dict})
    return data


def find_csv_seperator():
    ac = AccountConfiguration.objects.first()
    if ac.api_csv_separator:
        csv_separator = ac.api_csv_separator
    else:
        csv_separator = DEFAULT_CSV_SEPARATOR
    print("*** csv_separator *** ", csv_separator)
    return csv_separator
