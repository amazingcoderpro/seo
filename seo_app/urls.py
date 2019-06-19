from django.conf.urls import url, include
from seo_app.views import shopify_auth

v1_urlpatterns = [

]

auth_urlpatterns = [
    url(r'shopify/callback/$', shopify_auth.ShopifyCallback.as_view()),
    url(r'shopify/ask_permission/$', shopify_auth.ShopifyAuthView.as_view()),
]

urlpatterns = [
    url(r'^v1/', include(v1_urlpatterns)),
    url(r'^v1/auth/', include(auth_urlpatterns)),
]