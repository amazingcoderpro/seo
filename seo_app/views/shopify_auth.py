from django.http import HttpResponseRedirect

from rest_framework.views import APIView
from seo_app import models
from seo_app.utils import random_code
from rest_framework.response import Response
from sdk.shopify.shopify_oauth_info import ShopifyBase

from sdk.shopify.get_shopify_products import ProductsApi
from sdk.shopify import shopify_oauth_info


class ShopifyCallback(APIView):
    """shopify 回调接口"""
    def get(self, request):
        code = request.query_params.get("code", None)
        shop = request.query_params.get("shop", None)
        if not code or not shop:
            return HttpResponseRedirect(redirect_to="https://autometa.seamarketings.com/aut_state?state=2")
        shop_name = shop.split(".")[0]
        result = ShopifyBase(shop).get_token(code)
        if result["code"] != 1:
            return HttpResponseRedirect(redirect_to="https://autometa.seamarketings.com/aut_state?state=2")
        instance = models.Store.objects.filter(url=shop).first()
        if instance:
            instance.token = result["data"]
            instance.save()
            user_instance = models.User.objects.filter(id=instance.user_id).first()
            user_instance.is_active = 0
            user_instance.password = ""
            user_instance.save()
            email = user_instance.email
        else:
            store_data = {"name": shop_name, "url": shop, "token": result["data"]}
            instance = models.Store.objects.create(**store_data)
            info = ProductsApi(access_token=result["data"], shop_uri=shop).get_shop_info()
            email = info["data"]["shop"]["email"]
            user_data = {"username": shop, "email": email, "is_active": 0, "code": random_code.create_random_code(6, True)}
            user_instance = models.User.objects.create(**user_data)
            instance.user = user_instance
            instance.email = email
            instance.save()
        return HttpResponseRedirect(redirect_to="https://autometa.seamarketings.com/shopfy_regist?shop={}&email={}&id={}".format(shop, email, user_instance.id))


class ShopifyAuthView(APIView):
    """shopify 授权页面"""
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # 获取get请求的参数
        shop_uri = request.query_params.get("shop", None)
        if not shop_uri:
            return Response({"message": "no shop"})
        # shop_uri = shop_name + ".myshopify.com"
        permission_url = shopify_oauth_info.ShopifyBase(shop_uri).ask_permission(shop_uri)
        return HttpResponseRedirect(redirect_to=permission_url)