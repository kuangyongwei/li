from django.contrib import admin

# Register your models here.
from sm_order.models import Payment, Transport, CollectAddress, OrderInfo, OrderGoods


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ["name", "money"]


@admin.register(CollectAddress)
class CollectAddressAdmin(admin.ModelAdmin):
    list_display = ["collectperson", "collectphone", "hcity", "hproper", "harea", "collectbrief", "isDefault"]
    list_display_links = ["collectperson", "collectphone"]
    search_fields = ["collectphone","hcity", "hproper", "harea"]


@admin.register(OrderInfo)
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ["user","receivename","ordernumber", "ordermoney","receiveaddress","orderstatus", "transportway","paymoney",]


@admin.register(OrderGoods)
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ["orderto", "goods_sku", "goodsprice", "goodscount"]






