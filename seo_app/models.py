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
        db_table = 'user'
        ordering = ["-id"]


class Store(models.Model):
    """店铺表"""
    name = models.CharField(blank=True, null=True, max_length=255, verbose_name="店铺名称")
    url = models.CharField(blank=True, null=False, max_length=255, unique=True, verbose_name="店铺URL")
    #uri = models.CharField(blank=True, null=True, max_length=255, unique=True, verbose_name="店铺唯一标示")
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        blank=True,
    )
    token = models.CharField(blank=True, null=True, max_length=255, verbose_name="账号使用标识")
    money_format = models.CharField(blank=True, null=True, max_length=255, verbose_name="店铺money标识")
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, blank=True, null=True, unique=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'store'
        ordering = ["-id"]


class Product(models.Model):
    """产品表"""
    domain = models.CharField(max_length=255, blank=True, null=True, verbose_name="产品domain")
    uuid = models.CharField(max_length=64, verbose_name="产品唯一标识")
    description = models.TextField(blank=True, null=True, max_length=255, verbose_name="产品描述")
    sku = models.CharField(max_length=255, blank=True, null=True,verbose_name="产品sku")
    type = models.CharField(db_index=True, blank=True, null=True,max_length=255,  verbose_name="产品类型")
    title = models.TextField(blank=True, null=True, verbose_name="产品title")
    price = models.CharField(db_index=True, blank=True, null=True, max_length=255, verbose_name="产品价格")
    variants = models.TextField(blank=True, null=True, verbose_name="产品variants")
    meta_title = models.TextField(blank=True, null=True, verbose_name="产品meta_title")
    meta_description = models.TextField(blank=True, null=True, verbose_name="产品meta_description")
    remark_title = models.TextField(blank=True, null=True, verbose_name="产品title_remark")
    remark_description = models.TextField(blank=True, null=True, verbose_name="产品description_remark")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING)
    state_choices = ((0, '新产品'), (1, '待发布'), (2, '已发布'), (3, '发布失败'))
    thumbnail = models.TextField(verbose_name="缩略图", default=None, blank=True, null=True)
    state = models.SmallIntegerField(db_index=True, choices=state_choices, default=1, verbose_name="产品发布状态")
    error_text = models.TextField(blank=True, null=True, verbose_name="发布错误信息")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        unique_together = ("uuid", "store")
        db_table = 'product'
        ordering = ["id"]


class Collection(models.Model):
    """类目表"""
    uuid = models.CharField(max_length=64, verbose_name="类目唯一标识")
    address = models.CharField(max_length=255, verbose_name="类目地址")
    meta_title = models.CharField(blank=True, null=True, max_length=255, verbose_name="类目meta_title")
    meta_description = models.TextField(blank=True, null=True, verbose_name="类目meta_description")
    remark_title = models.TextField(blank=True, null=True, verbose_name="产品title_remark")
    remark_description = models.TextField(blank=True, null=True, verbose_name="产品description_remark")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING)
    error_text = models.TextField(blank=True, null=True, verbose_name="发布错误信息")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # managed = False
        unique_together = ("uuid", "store")
        db_table = 'collection'
        ordering = ["-id"]