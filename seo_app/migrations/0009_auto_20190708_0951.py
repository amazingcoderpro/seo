# Generated by Django 2.1 on 2019-07-08 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_app', '0008_auto_20190706_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='meta_title',
            field=models.TextField(blank=True, max_length=255, null=True, verbose_name='产品meta_title'),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.TextField(blank=True, db_index=True, max_length=255, null=True, verbose_name='产品title'),
        ),
    ]
