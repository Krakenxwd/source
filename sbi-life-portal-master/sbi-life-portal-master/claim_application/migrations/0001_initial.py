# Generated by Django 4.1.9 on 2023-10-20 08:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationDocument',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='File Name')),
                ('file', models.FileField(blank=True, null=True, upload_to='', verbose_name='File')),
                ('mime_type', models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='Mime Type')),
                ('num_pages', models.IntegerField(default=0, editable=False)),
                ('source_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Source Name')),
                ('preprocessed_file', models.FileField(blank=True, editable=False, null=True, upload_to='', verbose_name='Pre Processed File')),
                ('is_processed', models.BooleanField(default=False)),
                ('is_validated', models.BooleanField(default=False)),
                ('reason', models.TextField(blank=True, null=True)),
                ('job_started_at', models.DateTimeField(blank=True, null=True)),
                ('job_completed_at', models.DateTimeField(blank=True, null=True)),
                ('hash', models.CharField(blank=True, max_length=255, null=True)),
                ('marked_for_training', models.BooleanField(default=False)),
                ('marked_for_reviewed', models.BooleanField(default=False)),
                ('json_response', models.FileField(blank=True, null=True, upload_to='', verbose_name='Json Response')),
                ('status', models.CharField(choices=[('queued', 'In Queue'), ('processing', 'Processing'), ('completed', 'Success'), ('deleted', 'Deleted'), ('error', 'Error')], default='queued', max_length=50)),
                ('validation_status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('need_review', 'Need Review')], default='pending', max_length=50)),
                ('mode', models.CharField(choices=[('web', 'WEB'), ('api', 'API'), ('zip', 'ZIP'), ('sftp', 'SFTP'), ('email_reader', 'Email Reader')], default='web', max_length=50)),
                ('configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicatipn_documents', to='master.extractionconfiguration')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created_by_related', related_query_name='%(app_label)s_%(class)ss_created_by', to=settings.AUTH_USER_MODEL)),
                ('master_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='master_types', to='master.mastertype')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', related_query_name='%(app_label)s_%(class)ss_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('number', models.PositiveIntegerField(editable=False)),
                ('width', models.FloatField(editable=False)),
                ('height', models.FloatField(editable=False)),
                ('pre_processed_file', models.FileField(blank=True, null=True, upload_to='pdf')),
                ('file', models.FileField(blank=True, null=True, upload_to='pdf')),
                ('pre_processed_image', models.FileField(blank=True, null=True, upload_to='images')),
                ('image', models.FileField(blank=True, null=True, upload_to='images')),
                ('is_processed', models.BooleanField(default=False)),
                ('job_started_at', models.DateTimeField(blank=True, null=True)),
                ('job_completed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('queued', 'In Queue'), ('processing', 'Processing'), ('completed', 'Success'), ('error', 'Error')], default='queued', max_length=50)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created_by_related', related_query_name='%(app_label)s_%(class)ss_created_by', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='claim_application.applicationdocument')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', related_query_name='%(app_label)s_%(class)ss_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TempDumpFilesLog',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('json_response', models.JSONField(blank=True, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('extra_params', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('queued', 'Queued'), ('processing', 'Processing'), ('completed', 'Success'), ('error', 'Error')], default='queued', max_length=50)),
                ('file_type', models.CharField(blank=True, choices=[('excel', 'Excel'), ('csv', 'Csv')], max_length=50, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('w_min', models.FloatField(blank=True, default=0, null=True)),
                ('w_max', models.FloatField(blank=True, default=0, null=True)),
                ('h_min', models.FloatField(blank=True, default=0, null=True)),
                ('h_max', models.FloatField(blank=True, default=0, null=True)),
                ('word', models.CharField(blank=True, max_length=1024, null=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='words', to='claim_application.page')),
            ],
        ),
        migrations.CreateModel(
            name='SingleDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='File Name')),
                ('file', models.FileField(blank=True, null=True, upload_to='', verbose_name='File')),
                ('mime_type', models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='Mime Type')),
                ('num_pages', models.IntegerField(default=0, editable=False)),
                ('file_password', models.CharField(blank=True, max_length=255, null=True, verbose_name='File Password')),
                ('size', models.CharField(blank=True, max_length=50, null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created_by_related', related_query_name='%(app_label)s_%(class)ss_created_by', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='single_documents', to='claim_application.applicationdocument')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', related_query_name='%(app_label)s_%(class)ss_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReProcessDocumentEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('status', models.CharField(choices=[('open', 'Open'), ('close', 'Close')], default='close', max_length=50)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created_by_related', related_query_name='%(app_label)s_%(class)ss_created_by', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='re_run_events', to='claim_application.applicationdocument')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', related_query_name='%(app_label)s_%(class)ss_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PageLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('confidence', models.FloatField(default=0.0)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created_by_related', related_query_name='%(app_label)s_%(class)ss_created_by', to=settings.AUTH_USER_MODEL)),
                ('master_page_label', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='master.masterpagelabel')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', related_query_name='%(app_label)s_%(class)ss_modified_by', to=settings.AUTH_USER_MODEL)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_labels', to='claim_application.page')),
            ],
        ),
        migrations.CreateModel(
            name='PageField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('w_min', models.FloatField(blank=True, default=0, null=True)),
                ('w_max', models.FloatField(blank=True, default=0, null=True)),
                ('h_min', models.FloatField(blank=True, default=0, null=True)),
                ('h_max', models.FloatField(blank=True, default=0, null=True)),
                ('text', models.CharField(blank=True, max_length=1024, null=True)),
                ('value_text', models.CharField(blank=True, max_length=1024, null=True)),
                ('value_date', models.DateField(blank=True, null=True)),
                ('value_amount', models.FloatField(blank=True, null=True)),
                ('value_boolean', models.BooleanField(blank=True, null=True)),
                ('value_image', models.FileField(blank=True, null=True, upload_to='')),
                ('is_extracted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created_by_related', related_query_name='%(app_label)s_%(class)ss_created_by', to=settings.AUTH_USER_MODEL)),
                ('master_field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.masterfield')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', related_query_name='%(app_label)s_%(class)ss_modified_by', to=settings.AUTH_USER_MODEL)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagefields', to='claim_application.page')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceProcessReferenceId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('reference_id', models.CharField(blank=True, max_length=50, null=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created_by_related', related_query_name='%(app_label)s_%(class)ss_created_by', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice_process_reference_id', to='claim_application.applicationdocument')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', related_query_name='%(app_label)s_%(class)ss_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocumentReferenceTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(editable=False, max_length=256, verbose_name='File Name')),
                ('num_process', models.IntegerField(default=0)),
                ('num_pages', models.PositiveIntegerField(default=0, editable=False)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created_by_related', related_query_name='%(app_label)s_%(class)ss_created_by', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doc_references', to='claim_application.applicationdocument')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modified_by_related', related_query_name='%(app_label)s_%(class)ss_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='word',
            index=models.Index(fields=['page'], name='claim_appli_page_id_dbe214_idx'),
        ),
        migrations.AddIndex(
            model_name='word',
            index=models.Index(fields=['word'], name='claim_appli_word_ddb4b5_idx'),
        ),
        migrations.AddIndex(
            model_name='singledocument',
            index=models.Index(fields=['document'], name='claim_appli_documen_8ed53b_idx'),
        ),
        migrations.AddIndex(
            model_name='reprocessdocumentevents',
            index=models.Index(fields=['document'], name='claim_appli_documen_b8997c_idx'),
        ),
        migrations.AddIndex(
            model_name='pagelabel',
            index=models.Index(fields=['page'], name='claim_appli_page_id_694124_idx'),
        ),
        migrations.AddIndex(
            model_name='pagelabel',
            index=models.Index(fields=['master_page_label'], name='claim_appli_master__ab6793_idx'),
        ),
        migrations.AddIndex(
            model_name='pagefield',
            index=models.Index(fields=['page'], name='claim_appli_page_id_f36b1d_idx'),
        ),
        migrations.AddIndex(
            model_name='pagefield',
            index=models.Index(fields=['master_field'], name='claim_appli_master__791782_idx'),
        ),
        migrations.AddIndex(
            model_name='pagefield',
            index=models.Index(fields=['text'], name='claim_appli_text_ceecbe_idx'),
        ),
        migrations.AddIndex(
            model_name='pagefield',
            index=models.Index(fields=['value_text'], name='claim_appli_value_t_9ca733_idx'),
        ),
        migrations.AddIndex(
            model_name='pagefield',
            index=models.Index(fields=['value_date'], name='claim_appli_value_d_5055c5_idx'),
        ),
        migrations.AddIndex(
            model_name='pagefield',
            index=models.Index(fields=['value_amount'], name='claim_appli_value_a_e3a3ff_idx'),
        ),
        migrations.AddIndex(
            model_name='pagefield',
            index=models.Index(fields=['value_boolean'], name='claim_appli_value_b_997f89_idx'),
        ),
        migrations.AddIndex(
            model_name='pagefield',
            index=models.Index(fields=['is_active'], name='claim_appli_is_acti_89878f_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['document'], name='claim_appli_documen_63ed69_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['number'], name='claim_appli_number_65326c_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['width'], name='claim_appli_width_948930_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['height'], name='claim_appli_height_40005c_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['is_processed'], name='claim_appli_is_proc_77b122_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['job_started_at'], name='claim_appli_job_sta_e8141a_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['job_completed_at'], name='claim_appli_job_com_ebecfa_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['created_at'], name='claim_appli_created_a394e4_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['modified_at'], name='claim_appli_modifie_50cdaa_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['created_by'], name='claim_appli_created_126c32_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['modified_by'], name='claim_appli_modifie_de70c0_idx'),
        ),
        migrations.AddIndex(
            model_name='documentreferencetable',
            index=models.Index(fields=['document'], name='claim_appli_documen_dc99bf_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['configuration'], name='claim_appli_configu_e78164_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['preprocessed_file'], name='claim_appli_preproc_57d9c1_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['job_started_at'], name='claim_appli_job_sta_98811e_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['job_completed_at'], name='claim_appli_job_com_cc10af_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['hash'], name='claim_appli_hash_76d133_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['created_at'], name='claim_appli_created_85ab2f_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['modified_at'], name='claim_appli_modifie_ddf317_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['created_by'], name='claim_appli_created_954cae_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationdocument',
            index=models.Index(fields=['modified_by'], name='claim_appli_modifie_f5d167_idx'),
        ),
    ]