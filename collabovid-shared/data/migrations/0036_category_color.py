# Generated by Django 3.0.4 on 2020-06-05 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0035_auto_20200604_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='color',
            field=models.CharField(default='#F0F0F0', max_length=7),
        ),
    ]
