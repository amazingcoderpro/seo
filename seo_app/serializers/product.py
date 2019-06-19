from rest_framework import serializers
from seo_app import models


class ProductSerializer(serializers.ModelSerializer):
    """product"""
    class Meta:
        model = models.Product
        fields = "__all__"