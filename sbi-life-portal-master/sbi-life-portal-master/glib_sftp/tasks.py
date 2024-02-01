import io
from typing import List

import pysftp
from django.core.files import File
from django.template.loader import render_to_string
from weasyprint import HTML

from claim_application.models import ApplicationDocument, SingleDocument, Page, Claimant
from glib_sftp import models as sftp_models
from master.utility import split_and_create_pdf
from sbilife import celery_app as app


def upload_file_to_sftp(sftp_configuration, file_path, file_content, connection):
    sftp_request = sftp_models.SFTPRequest(sftp_configuration=sftp_configuration)
    sftp_request.save()
    sftp_request.upload_file(file_path, file_content, connection)


def generate_summary_pdf(document):
    """
        Generate a summary pdf of the detail page document.
    """
    context_dict = {'document': document}
    template = render_to_string('claim_application/detail/partials/cards_area_pdf.html', context=context_dict)
    result = io.BytesIO()
    HTML(string=template).write_pdf(result, presentational_hints=True)
    document.extracted_summary_pdf.save('summary.pdf', result, save=True)


def create_consolidated_pdfs(document):
    """
        Create a consolidated pdf of the pages with a unique page label.
    """
    dict_obj = {}
    for page in document.pages.exclude(page_labels__master_page_label__code='other'):
        if page and page.claimant and page.claimant.type == Claimant.NOMINEE:
            label = "{}_{}".format('nominee', page.page_labels.first().master_page_label.code)
        else:
            label = "other_{}".format(page.page_labels.first().master_page_label.code)
        pagefields_query = page.pagefields.filter(original_page_number__isnull=False)
        if pagefields_query.exists():
            page_number = pagefields_query.first().original_page_number
            dict_obj.setdefault(label, []).append(page_number)

    document.single_documents.filter(type=SingleDocument.PROCESSED).delete()
    for label, page_numbers in dict_obj.items():
        create_single_document(document, label, page_numbers)


def create_single_document(document, label, page_numbers):
    """
        Create a single documents with type Processed of all the uniques page labels.
    """
    single_doc = document.single_documents.create(type=SingleDocument.PROCESSED,
                                                  name="{}_{}.pdf".format(document.policy_number, label))
    file_data = File(io.BytesIO(split_and_create_pdf(document.file.open('rb').read(), page_numbers)),
                     name="{}_{}.pdf".format(document.policy_number, label))
    single_doc.file = file_data
    single_doc.save()


def upload_photo_to_sftp(document: ApplicationDocument, sftp_configuration, connection):
    """
        Upload a claimant photos to sftp.
        If claim form available then it's face image send to sftp else claimant wise photo send to sftp.
    """
    claim_form_pages: List[Page] = document.get_claim_form_pages()
    if claim_form_pages.exists():
        for claim_form_page in claim_form_pages:
            cf_image_field = claim_form_page.pagefields.filter(
                master_field__code='face').first() if claim_form_page else None
            if cf_image_field and cf_image_field.value_image:
                file_path = 'processed/{}_{}_photo.{}'.format(document.policy_number,
                                                              claim_form_page.get_page_label().code,
                                                              cf_image_field.value_image.name.split('.')[-1])
                file_content = cf_image_field.value_image.file
                upload_file_to_sftp(sftp_configuration, file_path, file_content, connection)
    else:
        for claimant in document.claimant_set.filter(type=Claimant.NOMINEE):
            for page in claimant.get_pages():
                image_field = page.pagefields.filter(
                    master_field__code='face').first() if page else None
                if image_field and image_field.value_image:
                    file_path = 'processed/{}_{}_photo.{}'.format(document.policy_number, claimant.customer_id,
                                                                  image_field.value_image.name.split('.')[
                                                                      -1])
                    file_content = image_field.value_image.file
                    upload_file_to_sftp(sftp_configuration, file_path, file_content, connection)
                    break


def upload_raw_processed_files_to_sftp(document, sftp_configuration):
    """
        Uploading raw and processed files to sftp server.
    """
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    connection = pysftp.Connection(host=sftp_configuration.host, port=int(sftp_configuration.port),
                                   username=sftp_configuration.username,
                                   password=sftp_configuration.password,
                                   cnopts=cnopts)

    for file_type in [SingleDocument.PROCESSED]:
        for doc in document.single_documents.filter(type=file_type):
            file_path = 'processed/{}'.format(doc.name)
            upload_file_to_sftp(sftp_configuration, file_path, doc.file, connection)

    if document.extracted_summary_pdf:
        file_path = 'processed/{}_{}'.format(document.policy_number,
                                             'summary.pdf')
        upload_file_to_sftp(sftp_configuration, file_path, document.extracted_summary_pdf.file, connection)
        document.log_sent_to_sftp()

    # Uploading a claimant photos to sftp
    upload_photo_to_sftp(document, sftp_configuration, connection)

    connection.close()


@app.task
def send_processed_files_to_sftp(doc_id):
    sftp_request = sftp_models.SFTPRequest()
    sftp_request.mark_as_initiated()
    try:
        document = ApplicationDocument.objects.get(id=doc_id)
        sftp_configurations = sftp_models.SFTPConfiguration.objects.filter(active=True)
        if sftp_configurations.exists():
            sftp_configuration = sftp_configurations.first()
            generate_summary_pdf(document)
            create_consolidated_pdfs(document)
            upload_raw_processed_files_to_sftp(document, sftp_configuration)
            sftp_request.mark_as_uploaded("For {} processed files uploaded to sftp.".format(document.name))
        else:
            message = "SFTP configurations not found."
            sftp_request.mark_as_error(message)
    except Exception as e:
        message = "Error: {}".format(str(e))
        sftp_request.mark_as_error(message)
        print(message)
