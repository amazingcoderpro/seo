from rest_framework import serializers
from seo_app import models


class ProductSerializer(serializers.ModelSerializer):
    """product"""

    domain = serializers.SerializerMethodField()
    class Meta:
        model = models.Product
        fields = (
            "id",
            "domain",
            "uuid",
            "description",
            "sku",
            "type",
            "title",
            "price",
            "variants",
            "remark_title",
            "remark_description",
            "thumbnail",
            "state"
        )

    def get_domain(self, obj):
        url = obj.domain.split("//")[1].split(".")[0] + ".com"
        return url.capitalize()


class ProductMotifySerializer(serializers.ModelSerializer):
    """修改product"""
    class Meta:
        model = models.Product
        fields = ("remark_title", "remark_description")
        extra_kwargs = {
            # 'title': {'write_only': True, "required":True},
            # 'description': {'write_only': True, "required":True},
            'remark_title': {'write_only': True, "required":True},
            'remark_description': {'write_only': True, "required":True}
        }