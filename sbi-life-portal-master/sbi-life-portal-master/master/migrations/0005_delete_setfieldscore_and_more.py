# Generated by Django 4.1.9 on 2023-12-27 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0004_digitalmasterfield_field_type_name_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SetFieldScore',
        ),
        migrations.RemoveField(
            model_name='digitalmasterfield',
            name='output_date_formate',
        ),
        migrations.RemoveField(
            model_name='digitalmasterfield',
            name='output_decimals_digit',
        ),
        migrations.RemoveField(
            model_name='digitalmasterfield',
            name='output_max_length',
        ),
        migrations.AddField(
            model_name='digitalmasterfield',
            name='description',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Scoring Description'),
        ),
        migrations.AddField(
            model_name='digitalmasterfield',
            name='do_scoring',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='digitalmasterfield',
            name='expected_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='digitalmasterfield',
            name='show_annotation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='digitalmasterfield',
            name='weightage',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
