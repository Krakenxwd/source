# Generated by Django 4.1.9 on 2023-10-20 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterpagelabel',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.mastertype'),
        ),
    ]
