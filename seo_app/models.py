import time,uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """系统用户表"""
    username = models.CharField(max_length=255, unique=True, verbose_name="账户")
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="账户邮箱")
    password = models.CharField(max_length=128, blank=True, null=True,  verbose_name="密码")
    code = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="用户唯一标识")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # managed = False
        db_table = 'user'
        ordering = ["-id"]


class Store(models.Model):
    """店铺表"""
    name = models.CharField(blank=True, null=True, max_length=255, verbose_name="店铺名称")
    url = models.CharField(blank=True, null=False, max_length=255, unique=True, verbose_name="店铺URL")
    uri = models.CharField(blank=True, null=False, max_length=255, unique=True, verbose_name="店铺唯一标示")
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        blank=True,
    )
    token = models.CharField(blank=True, null=True, max_length=255, verbose_name="账号使用标识")
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, blank=True, null=True, unique=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'store'
        ordering = ["-id"]


class Product(models.Model):
    """产品表"""
    sku = models.CharField(db_index=True, max_length=255, verbose_name="产品标识符")
    domain = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品domain")
    uuid = models.CharField(max_length=64, verbose_name="产品唯一标识", unique=True)
    name = models.CharField(db_index=True, max_length=255, verbose_name="产品名称")
    type_choices = ((0, '111'), (1, '222'), (2, '333'))
    type = models.SmallIntegerField(choices=type_choices, default=0, verbose_name="产品类型")
    state_choices = ((-1, '333'), (0, '111'), (1, '222'), (2, '333'))
    state = models.SmallIntegerField(choices=state_choices, default=0, verbose_name="产品状态")
    title = models.CharField(db_index=True, max_length=255, verbose_name="产品title")
    description = models.TextField(blank=True, null=True, verbose_name="产品描述")
    remark_title = models.TextField(blank=True, null=True, verbose_name="产品title_remark")
    remark_description = models.TextField(blank=True, null=True, verbose_name="产品description_remark")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING)

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # managed = False
        db_table = 'product'
        ordering = ["-id"]


class Variants(models.Model):
    """产品种类"""
    colour = models.CharField(db_index=True, max_length=255, verbose_name="产品颜色")
    size = models.CharField(db_index=True, max_length=255, verbose_name="产品尺寸")
    price = models.CharField(db_index=True, max_length=255, verbose_name="产品价格")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'product_variants'
        ordering = ["-id"]