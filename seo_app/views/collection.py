# -*- coding: utf-8 -*-
# Created by: Leemon7
# Created on: 2019/6/22
import datetime
from config import logger
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import generics, status

from sdk.shopify.get_shopify_products import ProductsApi
from seo_app import models
from seo_app.serializers import collection as collection_serializers
from seo_app.pageNumber.pageNumber import PNPagination
from seo_app.filters import collection as collection_filter


class CollectionViews(generics.ListAPIView):
    """collection"""
    queryset = models.Collection.objects.all()
    serializer_class = collection_serializers.CollectionSerializer
    pagination_class = PNPagination
    filter_backends = (collection_filter.CollectionFilter,)
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


class CollectionMotifyViews(generics.CreateAPIView):
    """修改类目信息"""
    queryset = models.Collection.objects.all()
    serializer_class = collection_serializers.CollectionMotifySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        collection_list = request.data.get("collection_list", None)
        if not collection_list:
            return Response({"detail": "collection_list cannot be empty"},status=status.HTTP_400_BAD_REQUEST)
        # 调用接口更新collection信息
        store = models.Store.objects.get(user_id=request.user)
        access_token, shop_uri, domain = store.token, store.uri, store.url
        api_obj = ProductsApi(access_token, shop_uri)
        for collection in eval(collection_list):
            collection_obj = models.Collection.objects.filter(pk=collection)
            title = request.data["remark_title"].replace("%Product Type%", collection_obj.first().meta_title).replace("%Domain%", domain)
            description = request.data["remark_description"].replace("%Product Type%", collection_obj.first().meta_description).replace("%Domain%", domain)
            title_res = api_obj.update_collection_seo_title(collection_obj.first().uuid, title)
            description_res = api_obj.update_collection_seo_description(collection_obj.first().uuid, description)
            if title_res["code"] == 1 and description_res["code"] == 1:
                collection_obj.update(remark_title=request.data["remark_title"], remark_description=request.data["remark_description"],
                                          update_time=datetime.datetime.now())
                logger.info("update collection({}) success.".format(collection_obj.first().meta_title))
            else:
                logger.info("update collection({}) failed. error is {}".format(collection_obj.first().meta_title, description_res["msg"] if title_res["code"]==1 else title_res["msg"]))
                return Response({"detail": description_res["msg"] if title_res["code"]==1 else title_res["msg"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "update all collections success."}, status=status.HTTP_200_OK)


