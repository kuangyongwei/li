from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.views import View
from django_redis import get_redis_connection

# 购物车的添加的功能
from sm_goods.models import GoodsSKU

# cartadd的路由
from sm_user.public import session_decorator


# 购物车模块
class ShoppingCartViews(View):
    @session_decorator
    def get(self, request):
        """
            1. 取出商品数据 redis sku_id count
            2. 从数据库中 取出完整的商品信息
            3. 计算总金额 和 总共的商品的件数量

            :param request:
            :return:
        """
        # 连接redis
        cnn = get_redis_connection('default')
        # 从redis中将所有的商品及数量取出来
        cart_key = "cart_%s" % request.session.get("ID")
        cart_list = cnn.hgetall(cart_key)  # 字典形式
        # print(cart_list)

        # 总金额 总数量
        total_money = 0
        total_count = 0
        # 存储所有的商品
        goodsList = []
        # 遍历字典
        for sku_id, count in cart_list.items():
            sku_id = int(sku_id)
            count = int(count)
            # 总数量增加
            total_count += count
            # 获取商品的信息
            goods = GoodsSKU.objects.get(pk=sku_id)
            # 对象上添加一个自定义的属性 count 当前商品的数量
            goods.count = count

            goodsList.append(goods)
            # 总金额
            total_money += goods.goodprice * count

        # 渲染数据
        context = {
            'goodsList': goodsList,
            'total_count': total_count,
            'total_money': total_money,
        }

        return render(request, "shoppingcart/shopcart.html", context)


# 购物车添加数据
class CartAddView(View):
    def post(self, request):
        # 1  前端通过ajax提交数据过来（以post的方式），获取数据（商品的sku_id，数量）
        # 2  保存到redis中
        # 3  验证是否有登录，如果没有登录，告诉ajax中的JS代码实现跳转到登录页面，location.href=url
        # 4 验证数据的合法性，必须都是整数
        # 5 验证商品是否存在
        # 6 验证库存是否足够

        sku_id = request.POST.get("sku_id")
        count = request.POST.get("count")

        # 验证是否登录
        if request.session.get("ID") is None:
            return JsonResponse({"error": 1, "msg": "没有登录，请登录"})

        # 重session中获取用户ID
        user_id = request.session.get("ID")

        # 验证数据的合法性
        try:
            sku_id = int(sku_id)
            count = int(count)
        except Exception as e:
            return JsonResponse({"error": 2, "msg": "数据不合法"})

        # 验证商品是否存在,
        try:
            sku_goods = GoodsSKU.objects.get(pk=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"error": 3, "msg": "商品不存在"})

        # 6 验证库存是否足够
        if sku_goods.goodsstock < count:
            return JsonResponse({"error": 4, "msg": "商品库存不够"})

        # 保存到redis数据库,配置:from  django_redis import get_redis_connection
        # 完成后,连接到redis
        cnn = get_redis_connection("default")  # 选着一个缓存配置
        # 将该用户的商品添加到redis中的购物车
        """
        HINCRBY key field increment
        为哈希表 key 中的域 field 的值加上增量 increment 。
        增量也可以为负数，相当于对给定域进行减法操作。
        如果 key 不存在，一个新的哈希表被创建并执行 HINCRBY命令。
        如果域 field 不存在，那么在执行命令前，域的值被初始化为 0 
        """
        cart_key = "cart_{}".format(user_id)
        cnn.hincrby(cart_key, sku_id, count)

        cart_total = 0
        vars = cnn.hvals(cart_key)
        if len(vars) > 0:
            for v in vars:
                cart_total += int(v)
        # 添加成功
        return JsonResponse({"error": 0, "msg": "添加购物车成功!", "cart_total": cart_total})


# 购物车减少数据
class CartDecrease(View):
    """
           1. 前端通过ajax post请求方式 将 sku_id (sku商品id) 一次减一个
           3. 验证是否登陆，如果没登陆，告诉ajax中的js代码实现跳转到登陆页面 location.href=url
           4. 验证数据的合法性，必须都为整数
           5. 验证商品是否存在
           2. 保存到redis
               配置是正确
               使用 hash对象 保存
               hset key 属性 值
               hset cart_user_id 商品id 数量
               >1 -1 如果商品数量等于 0 删除该商品
       :return:
       """

    def get(self, request):
        pass

    def post(self, request):
        sku_id = request.POST.get('sku_id')

        # 验证是否登陆
        if request.session.get("ID") is None:
            return JsonResponse({"error": 1, "msg": "没有登录,请先登录"})
        user_id = request.session.get("ID")

        # 验证数据的合法性
        try:
            sku_id = int(sku_id)
        except Exception as e:
            return JsonResponse({"error": 2, "msg": "数据不合法！"})

        # 验证商品是否存在
        try:
            sku_goods = GoodsSKU.objects.get(pk=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"error": 3, "msg": "商品不存在"})

        # 保存到redis 配置成功
        # 连接到redis
        cnn = get_redis_connection("default")  # 选择一个缓存配置
        # 将该用户的商品添加到redis中的购物车
        cart_key = "cart_%s" % user_id
        # 判断购物车中商品的数量是否 大于 1
        count = cnn.hget(cart_key, sku_id)
        # b'1'
        if int(count) > 1:
            cnn.hincrby(cart_key, sku_id, -1)
        else:
            cnn.hdel(cart_key, sku_id)

        # 计算现在购物车中的商品的数量
        cart_total = 0
        vars = cnn.hvals(cart_key)
        if len(vars) > 0:
            for v in vars:
                cart_total += int(v)
        # 添加成功
        return JsonResponse({"error": 0, "msg": "购物车中删除商品数量成功！", "cart_total": cart_total})
