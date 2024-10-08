# Generated by Django 2.1 on 2019-08-09 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_app', '0013_auto_20190708_0957'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='store',
            name='collection_description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='collection_description'),
        ),
        migrations.AddField(
            model_name='store',
            name='collection_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='collection_title'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_description',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='product_description'),
        ),
        migrations.AddField(
            model_name='store',
            name='product_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='product_title'),
        ),
    ]
