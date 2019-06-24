# -*- coding: utf-8 -*-
# Created by: Leemon7
# Created on: 2019/6/22
# Function:
from rest_framework import serializers

from seo_app import models


class CollectionSerializer(serializers.ModelSerializer):
    """collection"""
    domain = serializers.CharField(source="store.url", read_only=True)

    class Meta:
        model = models.Collection
        fields = ("id", "uuid", "meta_title", "meta_description", "remark_title", "remark_description", "domain")


class CollectionMotifySerializer(serializers.ModelSerializer):
    """修改collection"""
    class Meta:
        model = models.Collection
        fields = ("remark_title", "remark_description")
        extra_kwargs = {
            'meta_title': {'write_only': True, "required":True},
            'meta_description': {'write_only': True, "required":True},
            'remark_title': {'write_only': True, "required":True},
            'remark_description': {'write_only': True, "required":True}
        }