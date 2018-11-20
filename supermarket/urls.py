"""supermarket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 全文搜索框架
    url(r'^search/', include('haystack.urls')),

    # 用户信息app路径
    url(r'^sm_user/', include("apps.sm_user.user_urls", namespace="sm_user")),
    # 商品信息app路径 sm_goods
    url(r'^sm_goods/', include("apps.sm_goods.goods_urls", namespace="sm_goods")),
    url(r'^sm_order/', include("apps.sm_order.order_urls", namespace="sm_order")),
    # 上传部件自动调用的上传地址
    url(r'^ckeditor/', include("ckeditor_uploader.urls")),
    # 购物车系统
    url(r'^shoppingcart/', include("shoppingcart.carts_urls", namespace="shoppingcart")),
]
