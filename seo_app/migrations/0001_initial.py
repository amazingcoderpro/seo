# Generated by Django 2.1 on 2019-06-22 06:07

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=255, unique=True, verbose_name='账户')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='账户邮箱')),
                ('password', models.CharField(blank=True, max_length=128, null=True, verbose_name='密码')),
                ('code', models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='用户唯一标识')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'user',
                'ordering': ['-id'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(blank=True, max_length=255, null=True, verbose_name='产品domain')),
                ('uuid', models.CharField(max_length=64, verbose_name='产品唯一标识')),
                ('sku', models.CharField(blank=True, max_length=255, null=True, verbose_name='产品sku')),
                ('type', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='产品类型')),
                ('title', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='产品title')),
                ('price', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='产品价格')),
                ('variants', models.TextField(blank=True, null=True, verbose_name='产品variants')),
                ('meta_title', models.CharField(blank=True, max_length=255, null=True, verbose_name='产品meta_title')),
                ('meta_description', models.TextField(blank=True, null=True, verbose_name='产品meta_description')),
                ('remark_title', models.TextField(blank=True, null=True, verbose_name='产品title_remark')),
                ('remark_description', models.TextField(blank=True, null=True, verbose_name='产品description_remark')),
                ('thumbnail', models.TextField(blank=True, default=None, null=True, verbose_name='缩略图')),
                ('state', models.SmallIntegerField(choices=[(0, '新产品'), (1, '待发布'), (2, '已发布'), (3, '发布失败')], db_index=True, default=1, verbose_name='产品发布状态')),
                ('error_text', models.TextField(blank=True, null=True, verbose_name='发布错误信息')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'product',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='店铺名称')),
                ('url', models.CharField(blank=True, max_length=255, unique=True, verbose_name='店铺URL')),
                ('uri', models.CharField(blank=True, max_length=255, unique=True, verbose_name='店铺唯一标示')),
                ('email', models.EmailField(blank=True, max_length=255, verbose_name='email address')),
                ('token', models.CharField(blank=True, max_length=255, null=True, verbose_name='账号使用标识')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'store',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='seo_app.Store'),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('uuid', 'store')},
        ),
    ]
