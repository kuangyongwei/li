from django.contrib import admin

# Register your models here.

# 商品分类绑定
from sm_goods.models import GoodsClassify, GoodsSPU, Unit, GoodsSKU, GoodsPicture, FirstBroadcast, FirstActivity, \
    ActivityArea, Activitygoods


@admin.register(GoodsClassify)
class ClassifyAdmin(admin.ModelAdmin):
    pass


@admin.register(GoodsSPU)
class SPUAdmin(admin.ModelAdmin):
    list_display = ["SPUname", "SPUdetail"]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


class SkuAdminInline(admin.TabularInline):
    model = GoodsPicture
    extra = 3


@admin.register(GoodsSKU)
class SkuAdmin(admin.ModelAdmin):
    inlines = [SkuAdminInline]
    list_display = ["id", "goodsname", "goodspu", "verboseid_name", "goodprice", "goodsunit", "goodsstock",
                    "goodssales", "goodsshow", "create_time"]

    list_display_links = ["id", "goodsname", "goodspu", "verboseid_name"]
    # 每页显示条数
    list_per_page = 14
    list_filter = ["goodsname", "goodprice"]
    search_fields = ["goodssales", "goodprice", "create_time"]

    # fieldsets = (
    #     ("基本信息", {"fields": (
    #     "id", "goodsname","goodsabstract", "goodprice", "goodsunit", "goodsstock", "goodssales", "goodsshow")}),
    #     ("详细信息", {"fields": ("logoaddress","goodspu", "verboseid_name")}),
    # )


# ================================================

# 将首页中的表添加到后台管理

# 首页轮播商品表
@admin.register(FirstBroadcast)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["firstname", "goodsSku"]


# 首页活动表
@admin.register(FirstActivity)
class UnitAdmin(admin.ModelAdmin):
    pass


# 首页活动专区位置
@admin.register(ActivityArea)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["areaname", "areadescribe"]


# 首页专区活动商品
@admin.register(Activitygoods)
class UnitAdmin(admin.ModelAdmin):
    pass
