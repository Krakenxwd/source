# Generated by Django 4.1.9 on 2023-12-26 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claim_application', '0009_applicationdocument_ref_json_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationdocumentlog',
            name='code',
            field=models.CharField(choices=[('APPLICATION_DOCUMENT_SUBMITTED', 'Application Document Submitted'), ('EXTRACTION_START', 'Extraction Start'), ('EXTRACTION_COMPLETE', 'Extraction Complete'), ('EXTRACTION_ERROR', 'Extraction Error'), ('APPLICATION_DOCUMENT_PROCESSED', 'Application Document Processed'), ('APPLICATION_DOCUMENT_INVALID', 'Application Document Invalid'), ('APPLICATION_DOCUMENT_ERROR', 'Application Document Error'), ('DOCUMENTS_RECIEVED_FROM_SFTP', 'Documents Recieved From SFTP'), ('DOCUMENTS_SENT_TO_SFTP', 'Documents Sent To SFTP'), ('VALIDATIONS_RUN_START', 'Validations Run Start'), ('VALIDATIONS_RUN_FINISH', 'Validations Run Finish')], default='APPLICATION_DOCUMENT_SUBMITTED', max_length=50),
        ),
    ]
