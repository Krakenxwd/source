import asyncio
import io
import json
import logging
import os
import shutil
import traceback
import uuid
from datetime import datetime, timedelta

import pandas as pd
from dexter.common.document import Document
from dexter.common.document import Page as DexterBasePage
from dexter.identity.extractor import IdentityExtractor
from dexter.sbi_life_processor.extractor import SbiClassifier
from django.conf import settings
from django.db import Error
from django.db.models import F
from django.utils import timezone

from claim_application.models import ApplicationDocument, DocumentReferenceTable, SingleDocument, Page, PageLabel, Word, \
    PageField, Claimant, ClaimantFields, FieldScore, TemporaryValidation, ValidationRuleEngine, ValidationConfiguration, \
    Export
from glib_sftp.tasks import send_processed_files_to_sftp
from claim_application.templatetags.htmlfilter import has_group
from claim_application.utils import close_rerun_process_events, upload_file_to_s3, download_directory_from_s3, \
    remove_file_from_dir, pandas_title_replacer, get_page_level_document_json_data, get_page_level_digital_json_data
from master.models import MasterPageLabel, MasterField, DigitalMasterField, AccountConfiguration
from sbilife.celery import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_old_data(document_id):
    document = ApplicationDocument.objects.get(id=document_id)
    document.claimant_set.all().delete()
    document.pages.all().delete()


def fill_document_detail(document: ApplicationDocument, data: json):
    path = os.path.join(settings.MEDIA_ROOT, str(document.id), 'document.json')
    with open(path, 'w') as f:
        json.dump(data, f)  # Serialize the JSON data and write it to the file
        f.seek(0)
        document.json_response = upload_file_to_s3(path)
        remove_file_from_dir(path)
    document.save()
    document.refresh_from_db()
    data = json.loads(document.json_response.read())
    document.preprocessed_file = upload_file_to_s3(data['preprocessed_pdf_path'])

    document.file = upload_file_to_s3(data['file_path'])
    document.mime_type = data['mime_type']
    document.is_processed = True
    document.num_pages = data['num_pages']
    document.save()
    document.refresh_from_db()
    return data


def update_document_json(document: ApplicationDocument, data: json):
    path = ''
    try:
        path = os.path.join(settings.MEDIA_ROOT, str(document.id), 'document.json')
        with open(path, 'w') as f:
            json.dump(data, f)  # Serialize the JSON data and write it to the file
            f.seek(0)
            document.json_response = upload_file_to_s3(path)
        document.save()
        document.refresh_from_db()
        return data
    except Exception as e:
        print("Error:", str(e))
    remove_file_from_dir(path)


def iterate_over_page_labels(page, page_obj, label_list):
    """
        identify front, back, get claimant id and get labels.
    """
    claimant_id_list = [str(claimant) for claimant in
                        Claimant.objects.filter(document=page_obj.document).values_list('id', flat=True)]
    for key, value in page['labels'].items():
        if key == 'FRONT' or key == 'BACK':
            page_obj.is_front = True if key == 'FRONT' else False
            page_obj.save()
        elif key in claimant_id_list:
            page_obj.claimant = Claimant.objects.get(id=key)
            page_obj.save()
        else:
            label_obj = MasterPageLabel.objects.filter(tag_name__iexact=key).first()
            if label_obj:
                label_list.append(PageLabel(page=page_obj,
                                            master_page_label=label_obj,
                                            confidence=value))


def save_label(page, page_obj):
    label_list = []
    if page['labels']:
        iterate_over_page_labels(page, page_obj, label_list)
        # refresh from db as if changes occur
        page_obj.refresh_from_db()

        if label_list:
            PageLabel.objects.bulk_create(label_list)
        else:
            PageLabel.objects.create(page=page_obj,
                                     master_page_label=MasterPageLabel.objects.get(tag_name='OTHER'), confidence=1)
    else:
        PageLabel.objects.create(page=page_obj,
                                 master_page_label=MasterPageLabel.objects.get(tag_name='OTHER'), confidence=1)


def save_word(page, page_obj):
    word_list = []
    for word in page['words']:
        word_list.append(Word(page=page_obj,
                              word=word['text'],
                              w_min=word['w_min'],
                              w_max=word['w_max'],
                              h_min=word['h_min'],
                              h_max=word['h_max']))
    if word_list:
        Word.objects.bulk_create(word_list)


def get_processed_fields_dict(page_dict):
    """
    remove duplicate field name and Prefered fields whose processed key present in labels.
    """
    keys_to_check = ['name']

    new_list = []

    for d in page_dict:
        if d['labels'].get('PROCESSED', ''):
            if any(all(d[k] == x[k] for k in keys_to_check) for x in new_list):
                continue
            new_list.append(d)
    return new_list


def save_page_field(page, page_obj):
    updated_list_dict_page_fields = get_processed_fields_dict(page['page_fields'])

    # found label
    found_code = [field['name'] for field in updated_list_dict_page_fields]
    for label in page_obj.page_labels.all():
        page_field_list = []
        page_field_score = []

        master_field_list = list(MasterField.objects.filter(page_label=label.master_page_label,
                                                            tag_name__in=found_code,
                                                            is_active=True).values_list('tag_name', 'data_type'))

        for field in updated_list_dict_page_fields:
            for tag_name, data_type in master_field_list:
                if field['name'] == tag_name:
                    mf = MasterField.objects.get(
                        tag_name=field['name'], page_label=label.master_page_label)
                    page_field_score.append(FieldScore(
                        page=page_obj,
                        master_field=mf,
                        score=round(field['labels']['SCORE'], 2) if 'SCORE' in field['labels'].keys() else None
                    ))

                    page_field_list.append(PageField(
                        page=page_obj,
                        original_page_number=field['labels'].get('ORIGINAL_PAGE_NUMBER', None),
                        master_field=mf,
                        w_min=field['w_min'],
                        w_max=field['w_max'],
                        h_min=field['h_min'],
                        h_max=field['h_max'],
                        is_active=True,
                        text=field['text'],
                        value_text=field['value_text'],
                        value_date=datetime.strptime(field['value_date'], '%d/%m/%Y').strftime('%Y-%m-%d') if field[
                            "value_date"] else None,
                        value_amount=field['value_amount'],
                        value_boolean=field['value_boolean'],
                        value_image=upload_file_to_s3(field['value_text']) if data_type == MasterField.IMAGE else None
                    ))
                    break

        master_field_list = MasterField.objects.filter(page_label=label.master_page_label,
                                                       is_active=True).exclude(tag_name__in=found_code)
        for master_field in master_field_list:
            page_field_list.append(PageField(
                page=page_obj,
                master_field=master_field,
                w_min=0,
                w_max=0,
                h_min=0,
                h_max=0,
                is_active=True,
                text='',
                value_text='',
                value_date=None,
                value_amount=None,
                value_boolean=None,
                value_image=None
            ))

            page_field_score.append(FieldScore(
                page=page_obj,
                master_field=master_field,
                score=None
            ))

        PageField.objects.bulk_create(page_field_list)
        FieldScore.objects.bulk_create(page_field_score)


def fill_page_detail(document: ApplicationDocument, data: json):
    for page in data['pages']:
        # Create Page Object
        page_obj = Page.objects.create(document=document,
                                       number=page['number'],
                                       width=page['width'],
                                       height=page['height'],
                                       pre_processed_file=upload_file_to_s3(page['preprocessed_pdf_path']),
                                       file=upload_file_to_s3(page['pdf_path']),
                                       pre_processed_image=upload_file_to_s3(page['preprocessed_image_path']),
                                       image=upload_file_to_s3(page['image_path'])
                                       )
        print('page created')

        number = page_obj.number
        # Save Page Label
        save_label(page, page_obj)
        print('{} page label saved'.format(number))

        # Save Page Word
        save_word(page, page_obj)
        print('{} page word saved'.format(number))

        # Save Page Field
        save_page_field(page, page_obj)
        print('{} page field saved'.format(number))

    return document


def fill_page_detail_single(document: Document, data: json, page_num):
    for page in data['pages']:
        if page['number'] == page_num:
            # Create Page Object
            page_obj = Page.objects.get(document=document,
                                        number=page['number'])

            # Save Page Field
            page_obj.pagefields.all().delete()
            save_page_field(page, page_obj)
            print('page field saved')

    return document


def post_process_digital_json_data(document_id):
    """
        Adding a yob to digital json data. now it create a yob field on claimant fields.
    """
    doc = ApplicationDocument.objects.get(id=document_id)
    if doc.digital_json_data:
        data = doc.digital_json_data
        for json_data_claimant_key in ['policy_holder_detail', 'policy_nominees_detail']:
            claimant_details = data.get(json_data_claimant_key, [])
            for claimant_dict in claimant_details:
                for code in ['yob']:
                    if DigitalMasterField.objects.filter(code=code, is_active=True).exists():
                        if claimant_dict.get('dob', ''):
                            claimant_dict['yob'] = claimant_dict['dob'].split('/')[-1]

        doc.digital_json_data = data
        doc.save()
    doc.refresh_from_db()


def fill_claimant_detail(document_id):
    doc = ApplicationDocument.objects.get(id=document_id)
    if doc.mode in [ApplicationDocument.API,
                    ApplicationDocument.SFTP] and doc.digital_json_data:
        data = doc.digital_json_data
        for json_data_claimant_key in ['policy_holder_detail', 'policy_nominees_detail']:
            if data.get(json_data_claimant_key, ''):
                claimant_details = data[json_data_claimant_key]
                for claimant_dict in claimant_details:
                    claimant_object = Claimant.objects.create(
                        document=doc,
                        type=Claimant.HOLDER if json_data_claimant_key == 'policy_holder_detail' else Claimant.NOMINEE,
                        customer_id=claimant_dict.get('client_id', '')
                    )
                    for k, v in claimant_dict.items():
                        for field in DigitalMasterField.objects.filter(code=k, is_active=True):
                            if field.data_type == DigitalMasterField.TEXT:
                                ClaimantFields.objects.create(claimant=claimant_object, digital_master_field=field,
                                                              text=v,
                                                              value_text=v)
                            elif field.data_type == DigitalMasterField.DATE and v:
                                ClaimantFields.objects.create(claimant=claimant_object, digital_master_field=field,
                                                              text=v,
                                                              value_date=datetime.strptime(v, '%d/%m/%Y'))


def get_reference_data(document_id):
    document = ApplicationDocument.objects.get(id=document_id)
    claimants = Claimant.objects.filter(is_active=True, document=document)

    reference_data = []
    for claimant in claimants:
        claimant_data_dict = {'ID': claimant.id}
        claimant_fields_data = list(
            ClaimantFields.objects.filter(claimant=claimant, digital_master_field__is_active=True).values(
                'digital_master_field__code', 'text'))
        for claimant_field_dict in claimant_fields_data:
            claimant_field_list = list(claimant_field_dict.values())
            code, text = claimant_field_list[0], claimant_field_list[1]

            # if text value is empty or None it exclude in reference data
            if text and isinstance(text, str) and text.strip() and len(text.strip()) > 0:
                claimant_data_dict[code] = text

        reference_data.append(claimant_data_dict)

    """
        Adding a address to digital json data.
        concate address line 1,2,3, state, city, pincode to address.
    """
    for ref_dict in reference_data:
        address_parts = [ref_dict.get(code, '') for code in
                         ['address_1', 'address_2', 'address_3', 'city', 'state', 'pincode']]
        address = ' '.join(address_parts)
        if address and address.strip() and len(address.strip()) > 0:
            ref_dict['address'] = ' '.join(address_parts)

    document.ref_json_data = reference_data
    return document.ref_json_data


def get_field_validation_weight():
    score_rule_list = list(
        DigitalMasterField.objects.filter(allow_weightage=True).values('tag_name', 'weightage'))
    result_dict = {}
    for score_rule_dict in score_rule_list:
        code = score_rule_dict.get('tag_name', '')
        score = score_rule_dict.get('weightage', '')
        if code and score:
            result_dict[code] = score
    return result_dict


def prepare_name_to_original_map():
    result = {}
    dmf_list_dict = list(DigitalMasterField.objects.filter(is_active=True).values('code', 'tag_name'))
    for dmf_dict in dmf_list_dict:
        result[dmf_dict['code']] = dmf_dict['tag_name']
    return result


def prepare_field_type_matching():
    result = {}
    name_match_data = list(
        DigitalMasterField.objects.filter(is_active=True, field_type_name__isnull=False).values('tag_name',
                                                                                                'field_type_name'))
    for name_match_dict in name_match_data:
        result[name_match_dict['tag_name']] = name_match_dict['field_type_name']
    return result


def sbv001(page_id, rule: ValidationRuleEngine):
    try:
        print("running SBV001")
        page = Page.objects.get(id=page_id)
        master_fields = page.get_active_fields()
        for master_field in master_fields:
            score_obj = DigitalMasterField.objects.filter(code=master_field.code, do_scoring=True,
                                                          is_active=True).first()
            if score_obj:
                expected_score = score_obj.expected_score if score_obj.expected_score else None

                if expected_score:
                    page_field_obj = page.pagefields.filter(master_field=master_field).first()
                    field_score_obj = page.field_scores.filter(master_field=master_field).first()
                    if page_field_obj:
                        if field_score_obj and field_score_obj.score:
                            if field_score_obj.score > expected_score:
                                TemporaryValidation.objects.create(
                                    status=TemporaryValidation.SUCCESS,
                                    page=page,
                                    field=master_field,
                                    reason="{} score more than threshold.".format(master_field.name),
                                    rule=rule
                                )
                            else:
                                TemporaryValidation.objects.create(
                                    status=TemporaryValidation.FAILED,
                                    page=page,
                                    field=master_field,
                                    reason="{} score less than Threshold.".format(master_field.name),
                                    rule=rule
                                )
                        else:
                            TemporaryValidation.objects.create(
                                status=TemporaryValidation.FAILED,
                                page=page,
                                field=master_field,
                                reason="{} score not available due to insufficient results.".format(master_field.name),
                                rule=rule
                            )
                    else:
                        TemporaryValidation.objects.create(
                            status=TemporaryValidation.FAILED,
                            page=page,
                            field=master_field,
                            reason="{} is not extracted from the document.".format(master_field.name),
                            rule=rule
                        )

                else:
                    TemporaryValidation.objects.create(
                        status=TemporaryValidation.FAILED,
                        page=page,
                        field=master_field,
                        reason="{} score not specified.".format(master_field.name),
                        rule=rule
                    )
    except Exception as e:
        print(" SBV001 Exception >> ", str(e))


def cbv001(page_id, rule: ValidationRuleEngine):
    try:
        print("running CBV001")
        page = Page.objects.get(id=page_id)
        if page.get_active_fields().filter(code__in=['front', 'back', 'full'], is_active=True).exists():
            front_img_obj = page.pagefields.filter(master_field__code='front').first()
            back_img_obj = page.pagefields.filter(master_field__code='back').first()
            full_img_obj = page.pagefields.filter(master_field__code='full').first()

            if full_img_obj and full_img_obj.original_page_number:
                full_img_pg_num = full_img_obj.original_page_number
                if full_img_pg_num is not None:
                    TemporaryValidation.objects.create(
                        status=TemporaryValidation.SUCCESS,
                        page=page,
                        reason="Front and Back page are available.",
                        rule=rule
                    )
                else:
                    TemporaryValidation.objects.create(
                        status=TemporaryValidation.FAILED,
                        page=page,
                        reason="Front and Back page are not available.",
                        rule=rule
                    )
            elif front_img_obj and front_img_obj.original_page_number and back_img_obj and back_img_obj.original_page_number:
                front_img_pg_num = front_img_obj.original_page_number
                back_img_pg_num = back_img_obj.original_page_number
                if front_img_pg_num is not None and back_img_pg_num is not None:
                    TemporaryValidation.objects.create(
                        status=TemporaryValidation.SUCCESS,
                        page=page,
                        reason="Front and Back page are available.",
                        rule=rule
                    )
                else:
                    TemporaryValidation.objects.create(
                        status=TemporaryValidation.FAILED,
                        page=page,
                        reason="Front and Back page are not available.",
                        rule=rule
                    )
            elif back_img_obj and back_img_obj.original_page_number:
                TemporaryValidation.objects.create(
                    status=TemporaryValidation.FAILED,
                    page=page,
                    reason="Front page is not available.",
                    rule=rule
                )
            elif front_img_obj and front_img_obj.original_page_number:
                TemporaryValidation.objects.create(
                    status=TemporaryValidation.FAILED,
                    page=page,
                    reason="Back page is not available.",
                    rule=rule
                )
            else:
                TemporaryValidation.objects.create(
                    status=TemporaryValidation.FAILED,
                    page=page,
                    reason="Front and Back page are not available.",
                    rule=rule
                )
        else:
            print("Front, Back or Full is not available for {}".format(page.get_page_label().name))

    except Exception as e:
        print(" CBV001 Exception >> ", str(e))


@app.task
def run_validation_rules(document_id):
    document = ApplicationDocument.objects.get(id=document_id)
    validation_dict = {
        # SCORE Validation
        "SBV001": sbv001,
        "CBV001": cbv001
    }
    if document:
        vc = ValidationConfiguration.objects.filter().order_by('-created_at').first()
        if vc:
            print("----- VALIDATION START ----- ", datetime.now(), "-----")
            document.log_validations_run_start()
            validation_rules = vc.validation_rule_engine.filter(
                validation_action__in=[ValidationRuleEngine.MANDATORY, ValidationRuleEngine.OPTIONAL]).all()

            if vc.configuration_for == ValidationConfiguration.DOCUMENT:
                for claimant in document.claimant_set.all():
                    claimant.claimant_temp_validations.all().delete()
                for page in document.pages.all():
                    page.page_temp_validations.all().delete()
                    for field in page.pagefields.all():
                        field.pagefield_temp_validations.all().delete()

                    for rule in validation_rules:
                        validation_dict[rule.validation_code](
                            page_id=page.id, rule=rule)
        document.log_validations_run_finish()
        print("----- VALIDATION COMPLETE ----- ", datetime.now(), "-----")


@app.task
def process_document(document_id):
    document = ApplicationDocument.objects.get(id=document_id)
    document.status = ApplicationDocument.PROCESSING
    document.save()

    document.log_extraction_start()

    # creating a reference table
    defaults = {'name': document.name if document.name else '', 'num_pages': document.num_pages,
                'created_by': document.created_by, 'created_at': document.created_at}

    doc_ref, created = DocumentReferenceTable.objects.update_or_create(document=document,
                                                                       defaults=defaults)

    DocumentReferenceTable.objects.filter(
        document=document).update(num_process=F('num_process') + 1)

    process_reference_id = uuid.uuid4()
    document.document_process_reference_id.create(
        reference_id=process_reference_id)
    logger.info(
        f"Process Reference Id: {process_reference_id}, Initializing Process ApplicationDocument")

    document.refresh_from_db()
    document.status = ApplicationDocument.PROCESSING
    document.validation_status = ApplicationDocument.PENDING
    document.reason = ''
    document.job_started_at = timezone.now()
    document.save()
    logger.info(
        f"Process Reference Id: {process_reference_id}")
    dir_list = []

    try:
        subdocs = SingleDocument.objects.filter(document=document, type=SingleDocument.RAW)
        if document and subdocs.exists():

            # Clearing old data.
            try:
                logger.info(
                    f"Process Reference Id: {process_reference_id}, Clearing Old Data")
                clear_old_data(document_id)
                logger.info(
                    f"Process Reference Id: {process_reference_id}, Old Data Cleared")
            except Exception as e:
                error_msg = "Error while clearing the data"
                logger.error(
                    f"Process Reference Id: {process_reference_id}, {e}")
                raise Error(error_msg)

            logger.info(
                f"Process Reference Id: {process_reference_id}, Updating a digital json data.")
            post_process_digital_json_data(document_id)
            logger.info(
                f"Process Reference Id: {process_reference_id}, Digital json data updated.")

            # saving claimants details from digital json data
            logger.info(
                f"Process Reference Id: {process_reference_id}, Saving Claimants Details.")
            fill_claimant_detail(document.id)
            logger.info(
                f"Process Reference Id: {process_reference_id}, Claimant Level Data Saved")

            logger.info(
                f"Process Reference Id: {process_reference_id}, get the reference data and field validation weight.")
            reference_data = get_reference_data(document_id)
            result_dict = get_field_validation_weight()
            name_to_original_dict = prepare_name_to_original_map()
            field_type_matching_dict = prepare_field_type_matching()

            document.ref_json_data = reference_data
            document.score_json_data = result_dict
            document.name_to_original = name_to_original_dict
            document.field_type_matching = field_type_matching_dict
            document.save()

            document.refresh_from_db()
            try:
                logger.info(
                    f"Process Reference Id: {process_reference_id}, Running Pipeline based on file")

                doc_dir = os.path.join(settings.MEDIA_ROOT, "{}-docdir".format(document.id))
                working_dir = os.path.join(settings.MEDIA_ROOT, str(document.id))
                dir_list = [doc_dir, working_dir]
                if os.path.exists(doc_dir):
                    shutil.rmtree(doc_dir)
                os.makedirs(doc_dir, exist_ok=True)
                logger.info(
                    f"Process Reference Id: {process_reference_id}, adding files to {doc_dir}")

                for subdoc in subdocs:
                    path = os.path.join(doc_dir, subdoc.name)
                    with open(path, 'wb') as fh:
                        fh.write(subdoc.file.open('rb').read())
                        fh.seek(0)

                logger.info(
                    f"Process Reference Id: {process_reference_id}, added files successfuly")

                files = os.listdir(doc_dir)
                file_paths = [os.path.join(doc_dir, file) for file in files]
                max_threshold = AccountConfiguration.objects.first().max_threshold

                ext = SbiClassifier(working_dir=working_dir,
                                    files=file_paths, name_to_original_label=name_to_original_dict,
                                    field_type_matching=field_type_matching_dict,
                                    field_validation_weight=result_dict, ref_data=reference_data,
                                    overall_score_threshold=max_threshold)

                data = asyncio.run(ext())
                logger.info(
                    f"Process Reference Id: {process_reference_id}, Pipeline Completed")
            except Exception as e:
                logger.error(
                    f"Process Reference Id: {process_reference_id}, Pipeline Failed")
                raise RuntimeError('Pipeline failed', str(e))

            # saving document level data
            logger.info(f"Process Reference Id: {process_reference_id}, Saving ApplicationDocument Level Data")
            try:
                data = fill_document_detail(document, json.loads(data.json()))
            except Exception as e:
                raise Error(str(e))
            logger.info(f"Process Reference Id: {process_reference_id}, ApplicationDocument Level Data Saved")

            # saving page level data
            logger.info(
                f"Process Reference Id: {process_reference_id}, Saving Page Level Data")
            fill_page_detail(document, data)
            logger.info(
                f"Process Reference Id: {process_reference_id}, Page Level Data Saved")

            logger.info(
                f"Process Reference Id: {process_reference_id}, Run score rule validation")
            run_validation_rules(document.id)

            document.refresh_from_db()
            logger.info(f"Process Reference Id: {process_reference_id}, Send data to sftp")
            send_processed_files_to_sftp(document.id)

            logger.info(
                f"Process Reference Id: {process_reference_id}, closing the rerun process")
            close_rerun_process_events(document.id)

            document.refresh_from_db()
            # save document status to completed
            document.status = ApplicationDocument.COMPLETED
            document.job_completed_at = timezone.now()
            document.log_extraction_complete()
            document.save()
            document.log_processed()
        else:
            msg = "{} has no files present.".format(document.id)
            logger.error(msg)
            document.log_error(msg)
            raise Error(msg)
    except Exception as e:
        logger.error(
            f"Process Reference Id: {process_reference_id}, Error while processing the document --> {e}")

        # Build the error message from the traceback
        error_message = ''.join(traceback.format_tb(e.__traceback__)) + "\n{}".format(str(e))
        document.log_extraction_error(error_message)
        logger.info(
            f"Process Reference Id: {process_reference_id}, closing the rerun process")
        close_rerun_process_events(document.id)
        # save document status to error
        document.status = ApplicationDocument.ERROR
        document.job_completed_at = timezone.now()
        document.save()

    # removing working dir if exists
    for path in dir_list:
        # Note: path cannot be your base bir
        if os.path.exists(path) and path != os.path.join(settings.BASE_DIR):
            shutil.rmtree(path)


@app.task(name="process_single_page")
def process_single_page(document_id, page_id):
    document = ApplicationDocument.objects.get(id=document_id)
    page_obj = document.pages.filter(id=page_id).first()
    number = page_obj.number
    process_reference_id = uuid.uuid4()
    document.document_process_reference_id.create(
        reference_id=process_reference_id)
    logger.info(
        f"Process Reference Id: {process_reference_id}, Initializing Process Invoice for page number: {number}")
    page_obj.is_processed = False
    page_obj.status = Page.PROCESSING
    page_obj.save()
    document.is_processed = False
    document.status = ApplicationDocument.PROCESSING
    document.validation_status = ApplicationDocument.PENDING
    document.reason = ''
    document.save()
    logger.info(
        f"Process Reference Id: {process_reference_id}, Generating Params for page number: {number}")
    logger.info(
        f"Process Reference Id: {process_reference_id}, Params generated for page number: {number}")

    dir_list = []
    try:
        if document:
            try:
                logger.info(
                    f"Process Reference Id: {process_reference_id}, Initializing Pipeline for page number: {number}")
                logger.info(
                    f"Process Reference Id: {process_reference_id}, page {number} processing.")

                working_dir = os.path.join(settings.BASE_DIR, str(document.id))
                dir_list = [working_dir]

                page_pdf_path = os.path.join(settings.BASE_DIR, page_obj.file.name)

                download_directory_from_s3(str(document.id))

                new_doc = Document(name='merged.pdf', file_path=page_pdf_path, num_pages=1,
                                   is_scanned=True,
                                   mime_type='application/pdf')
                doc_json_path = os.path.join(settings.BASE_DIR, f'{str(document.id)}/document.json')
                page_label = page_obj.page_labels.first().master_page_label.tag_name

                with open(doc_json_path, 'r') as f:
                    data = json.loads(f.read())
                    for index, page in enumerate(data['pages']):
                        if page['number'] == number:
                            new_doc.pages = [DexterBasePage(**page)]
                            ext = IdentityExtractor(working_dir, file_path=page_pdf_path, document=new_doc,
                                                    detect_faces=True,
                                                    page_label=page_label)
                            resp, doc = asyncio.run(ext())
                            output = json.loads(doc.json())

                            # updating the document json
                            data['pages'][index].clear()
                            data['pages'][index] = {**output['pages'][0]}
                            break

                logger.info(
                    f"Process Reference Id: {process_reference_id}, Pipeline completed for page number: {number}")
            except Exception as e:
                logger.info(
                    f"Process Reference Id: {process_reference_id}, Pipeline failed for page number: {number}")
                raise RuntimeError('Pipeline failed', str(e))
            logger.info(
                f"Process Reference Id: {process_reference_id}, Filling the data for page number: {number}")
            data = update_document_json(document, data)
            logger.info(
                f"Process Reference Id: {process_reference_id}, Filled the data for page number: {number}")
            logger.info(
                f"Process Reference Id: {process_reference_id}, Filling the page detail for page number: {number}")
            fill_page_detail_single(document, data, number)
            logger.info(
                f"Process Reference Id: {process_reference_id}, Filled the page detail for page number: {number}")
            page = document.pages.filter(id=page_id).first()
            page.is_processed = True
            page.status = Page.COMPLETED
            page.save()
            document = ApplicationDocument.objects.get(id=document_id)
            document.is_processed = True
            document.status = ApplicationDocument.COMPLETED
            document.save()
    except Exception as e:
        logger.info(
            f"Process Reference Id: {process_reference_id}, Error while processing the single document -> {str(e)}")
        traceback.print_exc()
        page_obj.is_processed = False
        page_obj.status = Page.ERROR
        page_obj.save()
        document.status = ApplicationDocument.ERROR
        document.save()

    # removing working dir if exists
    for path in dir_list:
        if os.path.exists(path) and path != os.path.join(settings.BASE_DIR):
            shutil.rmtree(path)


@app.task(name='export_service')
def export_service(export_id):
    print("in export service: ", export_id)
    export = Export.objects.get(id=export_id)
    export.status = Export.PROCESSING
    export.save()
    try:
        file_type = export.file_type
        output_type = export.output_type

        object_list = []
        document_list = ApplicationDocument.objects.filter(created_at__range=[export.start_date,
                                                                              export.end_date + timedelta(seconds=1)])

        if export.created_by.is_superuser or has_group(export.created_by, 'admin'):
            document_list = document_list.order_by('created_at')
        else:
            document_list = document_list.filter(
                created_by=export.created_by).order_by('created_at')

        if output_type == Export.DOCUMENT:
            for document in document_list:
                object_list += get_page_level_document_json_data(document.id)
        elif output_type == Export.DIGITAL_JSON:
            for document in document_list:
                object_list += get_page_level_digital_json_data(document.id)

        if file_type == Export.EXCEL:
            df = pd.json_normalize(object_list)
            df = pandas_title_replacer(df)
            excel_content = io.BytesIO()
            sheet_name = "Exported {} Data".format(export.get_file_type_display())
            df.to_excel(excel_content, index=False, sheet_name=sheet_name)
            export.file.save("{}-export-data-{}.xlsx".format('sbi', uuid.uuid4().hex[0:7]),
                             excel_content, save=True)
        else:
            df = pd.json_normalize(object_list)
            df = pandas_title_replacer(df)
            output_buffer = io.BytesIO()
            df.to_csv(output_buffer, index=False, sep=str(export.csv_seperator))
            export.file.save("{}-export-data-{}.csv".format('sbi', uuid.uuid4().hex[0:7]), output_buffer,
                             save=True)
        export.status = Export.COMPLETED
        export.save()
    except Exception as e:
        export.message = "Error: {}".format(str(e))
        export.status = Export.ERROR
        export.save()
