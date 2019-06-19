from django.conf.urls import url, include
from seo_app.views import personal_center

v1_urlpatterns = [
    url(r'shopify/callback/$', personal_center.ShopifyCallback.as_view()),
    url(r'shopify/ask_permission/$', personal_center.ShopifyAuthView.as_view()),

]

urlpatterns = [
    url(r'^v1/', include(v1_urlpatterns)),
]