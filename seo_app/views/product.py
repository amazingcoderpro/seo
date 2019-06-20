import datetime
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import generics, status

from seo_app import models
from seo_app.serializers import product as product_serializers
from seo_app.pageNumber.pageNumber import PNPagination
from seo_app.filters import product as product_filter


class ProductViews(generics.ListAPIView):
    """Product"""
    queryset = models.Product.objects.all()
    serializer_class = product_serializers.ProductSerializer
    pagination_class = PNPagination
    filter_backends = (product_filter.ProductFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        is_paging = request.query_params.get("is_paging", None)
        if not is_paging:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductMotifyViews(generics.CreateAPIView):
    """修改产品信息"""
    queryset = models.Product.objects.all()
    serializer_class = product_serializers.ProductMotifySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def create(self, request, *args, **kwargs):
        product_list = request.data.get("product_list", None)
        if not product_list:
            return Response({"detail": "product_list cannot be empty"},status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        models.Product.objects.filter(id__in=eval(product_list)).update(remark_title=request.data["remark_title"],remark_description=request.data["remark_description"], update_time=datetime.datetime.now(), state=-1)
        return Response({}, status=status.HTTP_200_OK)


class ProductCategoresViews(generics.ListAPIView):
    """产品类目列表"""
    queryset = models.Product.objects.all()
    serializer_class = product_serializers.ProductSerializer
    pagination_class = PNPagination
    filter_backends = (product_filter.ProductFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        is_paging = request.query_params.get("is_paging", None)
        if not is_paging:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductCategoresMotifyViews(generics.CreateAPIView):
    """修改产品类目信息"""
    queryset = models.Product.objects.all()
    serializer_class = product_serializers.ProductMotifySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def create(self, request, *args, **kwargs):
        product_list = request.data.get("product_list", None)
        if not product_list:
            return Response({"detail": "product_list cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        models.Product.objects.filter(id__in=eval(product_list)).update(title=request.data["title"], description=request.data["description"], remark_title=request.data["remark_title"],remark_description=request.data["remark_description"])
        return Response({}, status=status.HTTP_200_OK)