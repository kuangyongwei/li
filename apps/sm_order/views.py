import datetime
import random

from django.db import transaction
from django.shortcuts import render
from django_redis import get_redis_connection
from django.views import View
from django.http import HttpResponse, JsonResponse

from sm_goods.models import GoodsSKU
from sm_order.forms import AddressAddForm
from sm_order.models import Transport, CollectAddress, OrderInfo, OrderGoods

from sm_user.models import UserInfo
from sm_user.public import session_decorator

"""
    确认订单页面， 即将生成订单的商品展示出来（价格，运输方式，收货地址）
        :param skus 代表的商品的sku_id:
                1. 获取商品id （获取一个 request.GET.get() 获取多个 request.GET.getlist() ）
                2. 查询商品信息
                3. 数量从redis购物车中获取
                4. 计算商品金额
                5. 计算总金额（商品总金额加运费）
    """


# 确认订单的详情
class OderDisplay(View):
    @session_decorator
    def get(self, request):
        # 用户的id
        user_id = request.session.get("ID")

        # 1.获取商品id的列表
        sku_ids = request.GET.getlist('skus')

        # 2. 查询商品信息
        goodsList = []  # 存储多个商品信息

        # 商品的总价格
        total_sku_price = 0

        # 3. 数量从redis购物车中获取
        cnn = get_redis_connection('default')
        cart_key = "cart_%s" % user_id

        for sku_id in sku_ids:
            # 获取了一个商品信息
            goods = GoodsSKU.objects.get(pk=sku_id)
            # goods商品对象上添加一个新的属性 count 代表商品的数量
            count = cnn.hget(cart_key, sku_id)
            count = int(count)
            goods.count = count
            goodsList.append(goods)
            # 计算的商品的总金额
            total_sku_price += count * goods.goodprice

        # 查询配送方式
        transList = Transport.objects.filter(is_delete=False).order_by('money')

        # 计算总金额
        trans = transList.first()
        total_price = total_sku_price + trans.money

        # 当前用户收货地址的展示,展示默认收货地址
        defaultaddress = CollectAddress.objects.filter(is_delete=False, isDefault=True, user_id=user_id).first()

        # 渲染页面
        context = {
            'goodsList': goodsList,
            'total_sku_price': total_sku_price,
            # 全部配送方式集合
            'transList': transList,
            'total_price': total_price,
            'defaultaddress': defaultaddress
        }
        return render(request, 'sm_order/tureorder.html', context)

    def post(self, request):
        """保存订单信息到订单基本信息表 和 订单商品表中"""
        """
            1. 收货地址add_id
            2. 商品sku_ids(多个 request.POST.getlist("sku_ids"))
            3. 配送方式transport
        """
        # 用户的id
        user_id = request.session.get("ID")
        try:
            user = UserInfo.objects.get(pk=user_id)
        except UserInfo.DoesNotExist:
            return JsonResponse({"error": 1, "msg": "参数有误"})

        # 接收提交过来的信息并且判断
        # 商品sku_id(多个)的列表
        sku_ids = request.POST.getlist("sku_id")
        # 地址信息的id
        address_id = request.POST.get("address_id")
        # 运输方式的id
        transport = request.POST.get("transpot")
        if not all([sku_ids, address_id, transport]):
            return JsonResponse({"error": 2, "msg": "传递参数有误"})

        # 获取收货地址的信息
        try:
            receiveinfo = CollectAddress.objects.filter(is_delete=False, user_id=user_id).get(pk=address_id)
        except CollectAddress.DoesNotExist:
            return JsonResponse({"error": 3, "msg": "收货地址不存在"})

        # 获取配送方式的信息
        try:
            transport = Transport.objects.filter(is_delete=False).get(pk=transport)
        except Transport.DoesNotExist:
            return JsonResponse({"error": 4, "msg": "配送方式不存在"})

        """
            1.添加订单基本信息表数据
            2.添加订单商品表数据
        """

        # 在保存到数据库的时候,需要设置一个保存点,以后可以可以回滚到该位置
        sid = transaction.savepoint()

        # 生成一个订单的编号
        order_num = "{}{}{}".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"), random.randint(1000, 9999),
                                    user_id)

        # 获得一个收货地址的信息,到收货地址表里面查询
        receiveaddress = "{}{}{}{}".format(receiveinfo.hcity, receiveinfo.hproper, receiveinfo.harea,
                                           receiveinfo.collectbrief)

        # 保存到数据库中
        try:
            orderinfo = OrderInfo.objects.create(
                ordernumber=order_num,
                user=user,
                receivename=receiveinfo.collectperson,
                receivephone=receiveinfo.collectphone,
                receiveaddress=receiveaddress,
                transportway=transport,
                transportprice=transport.money,
            )
        except:
            return JsonResponse({"error": 5, "msg": "创建订单基本信息失败"})
        # 计算订单的金额
        order_money = 0  # 订单金额
        """
        2.添加订单商品表数据
            商品数量 在redis
            商品价格 goodsSku表, 查询该表
        """
        # 连接redis
        cnn = get_redis_connection("default")
        cart_key = "cart_{}".format(user_id)
        for sku_id in sku_ids:
            # 获取商品信息
            try:
                good_sku = GoodsSKU.objects.select_for_update().get(pk=sku_id)
            except GoodsSKU.DoesNotExist:
                transaction.savepoint_rollback(sid)
                return JsonResponse({"error": 6, "msg": "商品不存在"})
            # 在redis中获取该商品的数量
            good_count = int(cnn.hget(cart_key, sku_id))

            # 得到该商品的数量后,判断库存是否足够
            if good_sku.goodsstock < good_count:
                transaction.savepoint_rollback(sid)
                return JsonResponse({"error": 7, "msg": "商品库存不足,请重新选购"})

            # 保存订单商品表的数据
            try:
                OrderGoods.objects.create(
                    orderto=orderinfo,
                    goods_sku=good_sku,
                    goodscount=good_count,
                    goodsprice=good_sku.goodprice,
                )
            except:
                transaction.savepoint_rollback(sid)
                return JsonResponse({"error": 8, "msg": "创建订单商品数据失败"})
            # 订单商品表保存成功, 说明该商品的库存需要减少
            good_sku.goodsstock -= good_count
            # 销量要增加
            good_sku.goodssales += good_count
            good_sku.save()

            # 开始计算订单的总价格
            order_money += good_sku.goodprice * good_count

        transport_money = transport.money
        # order_money += transport_money
        # 将订单的总价保存到数据库中
        try:
            orderinfo.ordermoney = order_money
            orderinfo.save()
        except:
            transaction.savepoint_rollback(sid)
            return JsonResponse({"error": 9, "msg": "更新订单总价失败"})

        # 数据保存后,需要清空购物车
        cnn.hdel(cart_key, *sku_ids)
        transaction.savepoint_commit(sid)
        return JsonResponse({"error": 0, "msg": "创建订单成功", "order_num": order_num})


# addressadd 添加地址信息
class AddressAddView(View):
    @session_decorator
    def get(self, request):
        return render(request, "sm_order/address.html", )

    def post(self, request):
        data = request.POST.dict()
        data["user_id"] = request.session.get("ID")
        add_form = AddressAddForm(data)
        if add_form.is_valid():
            # 数据合法,判断当前的地址是否为默认地址,如果是,就将其他地址全部设置为非默认地址(0)
            if add_form.cleaned_data.get("isDefault"):
                # 改变表里面的其他全部isDefault字段为0
                CollectAddress.objects.filter(user_id=request.session.get("ID")).update(isDefault=False)

            # 在保存的时候,因为表单里面user_id与用户信息关联,为ForeignKey,提交过来的信息没有user_id,
            # 所以保存的时候必须有用户ID
            add_form.instance.user_id = request.session.get("ID")
            add_form.save()
            return JsonResponse({"ok": 0, })
        else:
            return JsonResponse({"ok": 1, "errors": add_form.errors})


# 收货地址信息的展示
class AddressListView(View):
    @session_decorator
    def get(self, request):
        user_id = request.session.get("ID")
        # 查询得到当前用户的所有的地址信息
        addresslist = CollectAddress.objects.filter(user_id=user_id)
        context = {
            "addresslist": addresslist
        }
        return render(request, "sm_order/addresslist.html", context)

    def post(self, request):
        # 获取当前用户ID
        user_id = request.session.get("ID")
        # 重提交过来的数据中获取默认地址的id
        defadd_id = request.POST.get("defadd_id")
        # 修改用户收货地址表中的数据
        #     1.将全部收货信息的默认地址设置为False
        CollectAddress.objects.filter(user_id=user_id, is_delete=False).update(isDefault=False)

        #   2.将提交过来的id的默认值设置为True
        CollectAddress.objects.filter(user_id=user_id, is_delete=False, pk=defadd_id).update(isDefault=True)
        # 更新完毕,返回Js信息
        return JsonResponse({"ok": 0})


class OderPayView(View):
    def get(self, request):
        # 得到订单的编号
        order_num = request.GET.get("order_num")
        # 得到商品总价
        # 重session中获取用户ID
        uer_id = request.session.get("ID")
        # 查询订单信息
        orderinfo = OrderInfo.objects.filter(user_id=uer_id).get(ordernumber=order_num)
        # 查询商品信息
        ordergoods = orderinfo.ordergoods_set.all()
        total_money = orderinfo.ordermoney + orderinfo.transportprice

        # 传递到页面
        context = {
            "orderinfo": orderinfo,
            "ordergoods": ordergoods,
            "total_money": total_money,
        }
        return render(request, "sm_order/orderpay.html", context)

    def post(self, request):
        pass
