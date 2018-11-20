from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views import View

from sm_goods.models import GoodsClassify, GoodsSKU, GoodsSPU, GoodsPicture, Unit, FirstBroadcast, FirstActivity, \
    Activitygoods
from django_redis import get_redis_connection


class IndexViews(View):
    def get(self, request):
        # 查询首页轮播表全部信息
        firstaddress = FirstBroadcast.objects.all()
        # 查询活动表信息
        activetys = FirstActivity.objects.all()

        # 查询活动商品的信息为多对应多的关系
        a = []
        act = Activitygoods.objects.all()
        for i in act:
            a.append(i.id)

        # 遍历,得到活动商品的全部id,在查询sku里面的内容
        b = []
        bb = []
        for j in a:
            actt = Activitygoods.objects.filter(pk=j).first()
            # 得到查询集合
            actt_sku = actt.goodssku.all()
            for x in actt_sku:
                c = {"id": x.id, "name": x.goodsname, "img": x.logoaddress, "price": x.goodprice}
                bb.append(c)

        context = {
            "firstaddress": firstaddress,
            "activetys": activetys,
            "bb": bb,
        }
        return render(request, "sm_goods/index.html", locals())
# 产品分类
"""
    1  展示sku商品,子展示一种分类下的商品
    2  用户点击哪种分类就展示哪种分类 ---
    3  如果用户第一次进入页面,默认展示第一种分类产品

    排序:
        综合(id升序)     销量     价格降序    价格升序     新品(create_time)
        order_by(id)
        order_by(-id)
        
        排序的规则   0        1         2       3          4
        order_rule=["id","sale_num","-price","price","-create_time"]
"""

# 超市内容
class CategoryView(View):
    # 商品分类ID, 排序方式
    def get(self, request, cate_id=1, order=0):
        cate_id = int(cate_id)
        order = int(order)
        # 商品分类查询全部
        classifys = GoodsClassify.objects.filter(is_delete=0)
        # 根据传进来的  商品ID:cate_id,查询对应的商品
        manygoods = GoodsSKU.objects.filter(goodsverboseid=cate_id).filter(goodsshow=1)

        # 读取购物车中当前用户的商品总数
        cart_total = 0
        if request.session.get("ID"):
            cnn = get_redis_connection("default")
            cart_key = "cart_{}".format(request.session.get("ID"))
            vars = cnn.hvals(cart_key)
            if len(vars) > 0:
                for v in vars:
                    cart_total += int(v)

        # 定义一个列表,代表的是排序的规则
        order_rule = ["id", '-goodssales', '-goodprice', 'goodprice', '-create_time']

        # 获取当前应该是属于哪种排序
        current_order_rule = order_rule[order]
        # 将商品信息进行该有的排序
        manygoods = manygoods.order_by(current_order_rule)
        context = {
            # 商品分类信息
            "classifys": classifys,
            # 当前id包含的商品
            "manygoods": manygoods,
            "cate_id": cate_id,
            "order": order,
            "cart_total":cart_total
        }
        return render(request, "sm_goods/category.html", context=context)


# 商品详情
class DetailViews(View):
    def get(self, request, sku_id):
        # 1  首先获取spuid的值,方便查询SPU表数据
        sku_id = int(sku_id)
        # 3  再查询sku表中的数据,也一并传入html中
        goodssku = GoodsSKU.objects.filter(pk=sku_id).first()

        # # 2  根据得到的spuid,查询spu表,得到spu名称及详情
        # goodsspu = goodssku.

        # 4 根据商品,查询商品相册表GoodsPicture中的图片位置
        # goodsskuid = goodssku.id  # 商品id,得到商品介绍图片
        # goodspicture = goodssku.goodspicture_set.all().values()

        # 得到商品单位的id,查询单位名称
        # goodsunitid = goodssku.goodsunit_id  # 商品单位id
        # goodsunit = Unit.objects.filter(id=goodsunitid).first()

        context = {
            # "goodsspu": goodsspu,  # 商品spu
            "goodssku": goodssku,  # 商品sku
            # "goodspicture": goodspicture,  # 商品图片集合
            # "goodsunit": goodsunit,  # 商品单位

        }
        return render(request, "sm_goods/detail.html", context=context)

    def post(self, request):
        pass
