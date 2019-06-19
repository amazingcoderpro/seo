
from rest_framework import generics
from seo_app import models
from seo_app.serializers import product as product_serializers

from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class ProductViews(generics.ListAPIView):
    """Product"""
    queryset = models.Product.objects.all()
    serializer_class = product_serializers.ProductSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)