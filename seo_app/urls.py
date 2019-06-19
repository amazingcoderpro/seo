from django.conf.urls import url, include
from seo_app.views import shopify_auth, personal_center

# 公共中心 `/v1/auth/`
v1_urlpatterns = [

]

# 认证中心 `/v1/auth/`
auth_urlpatterns = [
    url(r'shopify/callback/$', shopify_auth.ShopifyCallback.as_view()),
    url(r'shopify/ask_permission/$', shopify_auth.ShopifyAuthView.as_view()),
]

# 用户中心 `/v1/account/`
account_urlpatterns = [
    # 注册 登陆
    url(r'^login/$', personal_center.LoginView.as_view()),
    # shopfy注册设置密码-->注册
    url(r'^set_password/(?P<pk>[0-9]+)/$', personal_center.SetPasswordView.as_view()),
    # 登陆状态下设置密码
    url(r'^set_passwords/(?P<pk>[0-9]+)/$', personal_center.SetPasswordsView.as_view()),
]


urlpatterns = [
    url(r'^v1/account/', include(account_urlpatterns)),
    url(r'^v1/auth/', include(auth_urlpatterns)),
    url(r'^v1/', include(v1_urlpatterns)),
]