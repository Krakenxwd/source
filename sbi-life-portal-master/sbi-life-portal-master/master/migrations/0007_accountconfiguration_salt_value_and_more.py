# Generated by Django 4.1.9 on 2023-12-28 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0006_digitalmasterfield_output_date_formate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountconfiguration',
            name='salt_value',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='accountconfiguration',
            name='secret_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]