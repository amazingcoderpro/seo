# Generated by Django 2.1 on 2019-07-08 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_app', '0011_auto_20190708_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='产品title'),
        ),
    ]
