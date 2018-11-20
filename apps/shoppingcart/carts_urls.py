from django.conf.urls import url

from shoppingcart.views import ShoppingCartViews, CartAddView, CartDecrease

urlpatterns = [
    # 进入购物车
    url(r'^$', ShoppingCartViews.as_view(), name="shoppingcart"),

    # 购物车添加数据
    url(r'^cartadd/$', CartAddView.as_view(), name="cartadd"),

    # 减少购物车数据
    url(r'^cartdecrease/$', CartDecrease.as_view(), name="cartdecrease"),
]
