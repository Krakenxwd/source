import binascii
import datetime
import io
import os
import uuid
import zipfile

import magic
import pandas as pd
import pysftp
import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import F

from claim_application.models import ApplicationDocument, SingleDocument
from claim_application.tasks import process_document
from claim_application.utils import get_number_of_pages_sftp, get_file_size
from master.models import AccountConfiguration, MasterType
from master.models import ExtractionConfiguration
from mixins.models import TimestampMixin
from mixins.models import UUIDMixin


# Create your models here.

class SFTPConfiguration(UUIDMixin, TimestampMixin, models.Model):
    """
        SFTP Configuration
    """
    # START MAIN ---
    host = models.CharField("Host", max_length=250, null=True, blank=True)
    port = models.CharField("Port", max_length=250, null=True, blank=True)
    username = models.CharField(
        "Username", max_length=250, null=True, blank=True)
    password = models.CharField(
        "Password", max_length=250, null=True, blank=True)
    active = models.BooleanField(default=True)
    file_path = models.CharField(
        "File Path", max_length=250, null=True, blank=True)
    upload_path = models.CharField(
        "Upload File Path", max_length=250, null=True, blank=True)
    supported_file_extension = models.CharField(
        "Supported File Extension", max_length=250, null=True, blank=True)
    TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(
        choices=TIMEZONE_CHOICES, max_length=32, default='UTC')

    # END MAIN ---
    def __str__(self):
        return '{}'.format(self.host)

    def save(self, *args, **kwargs):
        try:
            email = settings.SFTP_BOT_EMAIL
            password = settings.ADMIN_PASSWORD
            if not User.objects.filter(email=email).exists():
                password = password if password else binascii.hexlify(os.urandom(20)).decode()
                user = User.objects.create_user(email, email, password)
                user.save()
        except Exception as e:
            print(f'error {str(e)}')
        super(SFTPConfiguration, self).save(*args, **kwargs)


class SFTPRequest(UUIDMixin, TimestampMixin, models.Model):
    """
        SFTP Request
    """
    sftp_configuration = models.ForeignKey(
        SFTPConfiguration, on_delete=models.SET_NULL, null=True, blank=True)

    INITIATED = 'initiated'
    UPLOADING = 'uploading'
    UPLOADED = 'uploaded'
    DOWNLOADING = 'downloading'
    DOWNLOADED = 'downloaded'
    ERROR = 'error'

    TEST_INITIATED = 'test_initiated'
    TEST_UPLOADING = 'test_uploading'
    TEST_UPLOADED = 'test_uploaded'
    TEST_DOWNLOADING = 'test_downloading'
    TEST_DOWNLOADED = 'test_downloaded'
    TEST_ERROR = 'test_error'

    SFTP_FILE_STATUS = (
        (INITIATED, 'Initiated'),
        (UPLOADING, 'Uploading'),
        (UPLOADED, 'Uploaded'),
        (DOWNLOADING, 'Downloading'),
        (DOWNLOADED, 'Downloaded'),
        (ERROR, 'Error'),
        (TEST_INITIATED, 'Test Initiated'),
        (TEST_UPLOADING, 'Test Uploading'),
        (TEST_UPLOADED, 'Test Uploaded'),
        (TEST_DOWNLOADING, 'Test Downloading'),
        (TEST_DOWNLOADED, 'Test Downloaded'),
        (TEST_ERROR, 'Test Error'),
    )

    status = models.CharField(choices=SFTP_FILE_STATUS,
                              max_length=20, default=INITIATED)
    message = models.TextField(null=True, blank=True)
    file = models.FileField(blank=True, null=True)

    def mark_as_initiated(self):
        self.message = ''
        self.status = self.INITIATED
        self.save()

    def mark_as_uploading(self, message=''):
        self.message = message
        self.status = self.UPLOADING
        self.save()

    def mark_as_uploaded(self, message=''):
        self.message = message
        self.status = self.UPLOADED
        self.save()

    def mark_as_downloading(self, message=''):
        self.message = message
        self.status = self.DOWNLOADING
        self.save()

    def mark_as_downloaded(self, message=''):
        self.message = message
        self.status = self.DOWNLOADED
        self.save()

    def mark_as_error(self, message=''):
        self.status = self.ERROR
        self.message = message
        self.save()

    def mark_as_testing_status(self, status=TEST_INITIATED, message=''):
        self.status = status
        self.message = message
        self.save()

    def save_file(self, file_name, file_size, sftp_file_object, time_stamp):
        message = ''
        doc_id = self.application_doc_id
        if self.sftp_configuration.supported_file_extension and \
                self.sftp_configuration.supported_file_extension.split(','):
            if file_name.endswith(tuple(self.sftp_configuration.supported_file_extension.split(','))):
                # getting a uploaded file time
                timezone = pytz.timezone(self.sftp_configuration.timezone)
                file_time_stamp = datetime.datetime.strptime(datetime.datetime.fromtimestamp(time_stamp)
                                                             .strftime('%Y-%m-%d %H:%M:%S'),
                                                             '%Y-%m-%d %H:%M:%S') \
                    .astimezone(timezone)

                # reduce the limit by 1
                if self.has_upload_limit:
                    AccountConfiguration.objects.all().update(
                        upload_limit=F('upload_limit') - 1)

                # get mime type like .pdf, .jpg etc
                mime_type = magic.from_buffer(
                    sftp_file_object.read(), mime=True)

                num_pages = get_number_of_pages_sftp(
                    sftp_file_object, mime_type)

                application_doc = ApplicationDocument.objects.get(id=doc_id)

                document = SingleDocument.objects.create(document=application_doc,
                                                         type=SingleDocument.RAW,
                                                         name=file_name,
                                                         size=file_size,
                                                         mime_type=mime_type,
                                                         num_pages=num_pages,
                                                         created_by=User.objects.get(email=settings.SFTP_BOT_EMAIL))
                sftp_file_object.seek(0)
                document.file.save(file_name, ContentFile(
                    sftp_file_object.read()), save=True)

                SFTPFile.objects.create(
                    document_reference=document, file_timestamp=file_time_stamp)
                message = "File processed successfully."
            else:
                message = "The file extension of the uploaded file {} does not match the provided extension.".format(
                    file_name)
                raise ValueError(message)
        else:
            message = "file extension not provided."

        self.process_file_log_dict[file_name] = message

    def process_zipfile(self, zipbytesio_obj, time_stamp):
        """
            process zipfile from the sftp server
        """
        with zipfile.ZipFile(zipbytesio_obj) as archive:
            zipfiles_list = archive.namelist()
            config = AccountConfiguration.objects.first()

            for file_name in zipfiles_list:
                bytesio_obj = io.BytesIO(archive.read(file_name))
                file_size = bytesio_obj.getbuffer().nbytes
                if config.has_upload_limit:
                    if config.upload_limit > 0:
                        self.has_upload_limit = True
                        self.save_file(file_name, file_size, bytesio_obj, time_stamp)
                    else:
                        raise PermissionError(
                            'Exceeded the limit for processing or permission for upload has been denied.')
                else:
                    self.save_file(file_name, file_size, bytesio_obj, time_stamp)

    def get_files(self, folder_name, doc_id):
        """
            Get files from SFTP
        """
        self.process_file_log_dict = {}
        self.mark_as_initiated()
        application_doc = ApplicationDocument.objects.get(id=doc_id)
        try:
            self.mark_as_downloading()
            if folder_name:
                conf_path = os.path.join(self.sftp_configuration.file_path, folder_name)
            else:
                conf_path = self.sftp_configuration.file_path

            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            connection = pysftp.Connection(host=self.sftp_configuration.host, port=int(self.sftp_configuration.port),
                                           username=self.sftp_configuration.username,
                                           password=self.sftp_configuration.password,
                                           cnopts=cnopts)

            # it check path exists and check the given path should be directory path not the file path
            if connection.exists(conf_path) and 'd' in str(connection.lstat(conf_path)).split()[0]:
                connection.cwd(conf_path)
                sftp_paths = connection.listdir()
                if len(sftp_paths) > 0:
                    self.application_doc_id = application_doc.id
                    for path in sftp_paths:
                        lstatout = str(connection.lstat(path)).split()[0]
                        file_name = path.split('/')[-1]
                        time_stamp = connection.stat(file_name).st_mtime
                        if 'd' in lstatout:
                            print("Directory not allowed.")
                        elif 'zip' in path.split('.'):
                            size = connection.stat(path).st_size
                            if size > 1e+8:
                                raise ValueError('{} zipfile is more than 100 mb'.format(file_name))
                            bytesio_obj = io.BytesIO(connection.open(path).read())
                            self.process_zipfile(bytesio_obj, time_stamp)
                        else:
                            size = get_file_size(connection.stat(path).st_size)
                            config = AccountConfiguration.objects.first()
                            bytesio_obj = connection.open(file_name)

                            # check the limit
                            if config.has_upload_limit:
                                if config.upload_limit > 0:
                                    self.has_upload_limit = True
                                    self.save_file(file_name, size, bytesio_obj, time_stamp)
                                else:
                                    self.mark_as_error(
                                        'Exceeded the limit for processing, you have no upload credits remaining.')
                                    break
                            else:
                                self.has_upload_limit = False
                                self.save_file(file_name, size, bytesio_obj, time_stamp)
                else:
                    self.mark_as_error("The path you specified does not contain any files.")
            else:
                self.mark_as_error("The specified path does not exist in the sftp server.")

            if self.status != SFTPRequest.ERROR:
                # process a document
                application_doc.log_sftp_received()
                process_document.delay(application_doc.id)
                sftp_message = self.save_the_output(application_doc.id)
                self.mark_as_downloaded(message=sftp_message)
            connection.close()
        except Exception as e:
            print("Error: " + str(e))
            self.mark_as_error(str(e))

    def save_the_output(self, doc_id):
        doc = ApplicationDocument.objects.get(id=doc_id)
        df = pd.DataFrame()
        message = ''
        if self.process_file_log_dict:
            total_files = len(list(self.process_file_log_dict.keys()))
            message = '{} files found'.format(total_files)

            df = pd.DataFrame(
                {'Files': list(self.process_file_log_dict.keys()),
                 'message': list(self.process_file_log_dict.values())})

            output_buffer = io.BytesIO()
            df.to_excel(output_buffer, sheet_name=f"Exported SFTP Files Name")

            self.file.save("{}-sftp-data-{}.xlsx".format(doc.policy_number, uuid.uuid4().hex[0:7]), output_buffer)

        message = 'File not found' if df.empty else message
        return message

    def get_files_test(self):
        """
            Test Get files from SFTP
        """
        file_name_list = []
        self.mark_as_testing_status(status=self.TEST_INITIATED, message='')
        try:
            self.mark_as_testing_status(
                status=self.TEST_DOWNLOADING, message='')
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            connection = pysftp.Connection(host=self.sftp_configuration.host, port=int(self.sftp_configuration.port),
                                           username=self.sftp_configuration.username,
                                           password=self.sftp_configuration.password,
                                           cnopts=cnopts)
            connection.cwd(self.sftp_configuration.file_path)
            files = connection.listdir()
            for file_name in files:
                if self.sftp_configuration.supported_file_extension and \
                        self.sftp_configuration.supported_file_extension.split(','):
                    if file_name.endswith(tuple(self.sftp_configuration.supported_file_extension.split(','))):
                        file_name_list.append(file_name)
            self.mark_as_testing_status(status=self.TEST_DOWNLOADED,
                                        message=f'{len(file_name_list)} files found --> {",".join(file_name_list)}')
            connection.close()
        except Exception as e:
            print("Error: " + str(e))
            self.mark_as_testing_status(status=self.TEST_ERROR, message=str(e))

    def mkdir_p(self, sftp, remote_directory):
        if remote_directory == '/':
            # absolute path so change directory to root
            sftp.chdir('/')
            return
        if remote_directory == '':
            # top-level relative directory must exist
            return
        try:
            sftp.chdir(remote_directory)  # sub-directory exists
        except IOError:
            dirname, basename = os.path.split(remote_directory.rstrip('/'))
            self.mkdir_p(sftp, dirname)  # make parent directories
            sftp.mkdir(basename)  # sub-directory missing, so created it
            sftp.chdir(basename)
            return True

    def upload_file(self, file_path, file_content, connection=None):
        """
            Upload file to SFTP
        """
        self.mark_as_initiated()
        try:
            file_dir_path, file_name = os.path.split(file_path.rstrip('/'))
            self.mark_as_uploading(message=f'Uploading file {file_name}')
            if not connection:
                cnopts = pysftp.CnOpts()
                cnopts.hostkeys = None
                connection = pysftp.Connection(host=self.sftp_configuration.host,
                                               port=int(self.sftp_configuration.port),
                                               username=self.sftp_configuration.username,
                                               password=self.sftp_configuration.password,
                                               cnopts=cnopts)
            upload_path = self.sftp_configuration.upload_path
            remote_dir_path = os.path.join(upload_path, file_dir_path)
            self.mkdir_p(connection, remote_dir_path)
            connection.putfo(flo=file_content, remotepath=file_name)
            self.mark_as_uploaded(
                message=f'File {file_name} uploaded successfully')

            if not connection:
                connection.close()
        except Exception as e:
            print("Error: " + str(e))
            self.mark_as_error(str(e))

    def upload_file_test(self, file_name='test.txt', file_content=None):
        """
            Test Upload file to SFTP
        """
        self.mark_as_testing_status()
        try:
            self.mark_as_testing_status(status=self.TEST_UPLOADING)
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            connection = pysftp.Connection(host=self.sftp_configuration.host, port=int(self.sftp_configuration.port),
                                           username=self.sftp_configuration.username,
                                           password=self.sftp_configuration.password,
                                           cnopts=cnopts)
            connection.cwd(self.sftp_configuration.upload_path)
            if not file_content:
                file_content = ContentFile(
                    'This is a test file', name=file_name)
            connection.putfo(flo=file_content, remotepath=file_name)
            self.mark_as_testing_status(
                status=self.TEST_UPLOADED, message='File Uploaded Successfully')
            connection.close()
        except Exception as e:
            print("Error: " + str(e))
            self.mark_as_testing_status(status=self.TEST_ERROR, message=str(e))


class SFTPFile(UUIDMixin, TimestampMixin, models.Model):
    """
        Customer SFTP File
    """
    # START MAIN ---

    document_reference = models.ForeignKey(SingleDocument, on_delete=models.CASCADE)
    file_timestamp = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_output_uploaded = models.BooleanField(default=False)

    # END MAIN ---

    def __str__(self):
        return self.document_reference.name
