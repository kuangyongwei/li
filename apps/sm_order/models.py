from django.db import models
from db.base_model import BaseModel

# Create your models here.


# 选着支付方式
from sm_user.models import UserInfo


# 支付方式
class Payment(BaseModel):
    """
        支付方式
    """
    pay_name = models.CharField(verbose_name='支付方式',
                                max_length=20
                                )

    class Meta:
        verbose_name = "支付方式"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.pay_name


# 快递/配送方式
class Transport(BaseModel):
    """
        配送方式
    """
    name = models.CharField(verbose_name='配送方式',
                            max_length=20
                            )
    money = models.DecimalField(verbose_name='金额',
                                max_digits=9,
                                decimal_places=2,
                                default=0
                                )

    class Meta:
        verbose_name = "配送方式"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 收货地址包含的信息
class CollectAddress(BaseModel):
    user = models.ForeignKey(to='sm_user.UserInfo', verbose_name="用户ID")
    collectperson = models.CharField(verbose_name="收货人", max_length=100)
    collectphone = models.CharField(verbose_name="收货人电话", max_length=11)
    hcity = models.CharField(verbose_name="省", max_length=100)
    hproper = models.CharField(verbose_name="市", max_length=100, blank=True, default='')
    harea = models.CharField(verbose_name="区", max_length=100, blank=True, default='')
    collectbrief = models.CharField(verbose_name="详细地址", max_length=255)
    isDefault = models.BooleanField(verbose_name="是否设置为默认", default=False, blank=True)

    class Meta:
        verbose_name = "收货地址管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.collectperson


# 创建订单信息表格
class OrderInfo(BaseModel):
    orderstatus_choices = (
        (0, '待付款'),
        (1, '退发货'),
        (2, '待收货'),
        (3, '待评价'),
        (4, '已完成'),
        (5, '取消订单'),
    )

    ordernumber = models.CharField(max_length=150, verbose_name="订单编号")
    ordermoney = models.DecimalField(verbose_name="订单金额", decimal_places=2, max_digits=7,default=0)
    user = models.ForeignKey(to=UserInfo, verbose_name="当前用户ID")
    receivename = models.CharField(
        verbose_name="收货人姓名", max_length=100)
    receivephone = models.CharField(verbose_name="收货人电话", max_length=11)
    receiveaddress = models.CharField(verbose_name="收货人地址", max_length=200)
    orderstatus = models.SmallIntegerField(
        verbose_name="订单状态",
        choices=orderstatus_choices,
        default=0, )
    transportway = models.ForeignKey(to="Transport", verbose_name="运输方式")
    transportprice = models.DecimalField(verbose_name="运送价格", max_digits=5, decimal_places=2, default=0)
    payway = models.ForeignKey(verbose_name="支付方式",
                               to="Payment",
                               null=True, blank=True)
    paymoney = models.DecimalField(verbose_name="实际支付金额",
                                   max_digits=7,
                                   decimal_places=2, default=0)
    description = models.CharField(verbose_name="备注说明", max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "订单基本信息表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ordernumber


# 订单商品表格
class OrderGoods(BaseModel):
    """订单商品表"""
    orderto = models.ForeignKey(to="OrderInfo", verbose_name="所属订单")
    goods_sku = models.ForeignKey(to='sm_goods.GoodsSKU', verbose_name="商品SKU")
    goodsprice = models.DecimalField(verbose_name="商品单价", max_digits=9, decimal_places=2, default=0)
    goodscount = models.IntegerField(verbose_name="订单商品数量", default=0)

    class Meta:
        verbose_name = "订单商品表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}-{}".format(self.orderto.ordernumber, self.goods_sku.goodsname)
