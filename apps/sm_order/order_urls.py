from django.conf.urls import url

from sm_order.views import OderDisplay, AddressAddView, AddressListView, OderPayView

urlpatterns = [
    url(r'^$', OderDisplay.as_view(), name="display"),

    url(r'^addressadd/$', AddressAddView.as_view(), name="addressadd"),
    # 收货地址全部信息的展示
    url(r'^addresslist/$', AddressListView.as_view(), name="addresslist"),
    # 订单支付页面
    url(r'^orderpay/$', OderPayView.as_view(), name="orderpay"),
]
