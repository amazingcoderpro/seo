from rest_framework import serializers
from seo_app import models


class ProductSerializer(serializers.ModelSerializer):
    """product"""
    class Meta:
        model = models.Product
        fields = "__all__"


class ProductMotifySerializer(serializers.ModelSerializer):
    """修改product"""
    class Meta:
        model = models.Product
        fields = ("title", "description", "remark_title", "remark_description")
        extra_kwargs = {
            # 'title': {'write_only': True, "required":True},
            # 'description': {'write_only': True, "required":True},
            'remark_title': {'write_only': True, "required":True},
            'remark_description': {'write_only': True, "required":True}
        }