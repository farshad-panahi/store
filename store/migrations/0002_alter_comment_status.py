# Generated by Django 5.0 on 2023-12-30 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='status',
            field=models.CharField(choices=[('W', 'WAITING'), ('A', 'APPROVED'), ('NA', 'NOT APPROVED')], default='W', max_length=2),
        ),
    ]
