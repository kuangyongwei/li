from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
# Create your models here.

from db.base_model import BaseModel


# 商品分类表
class GoodsClassify(BaseModel):
    # 分类名
    classifyname = models.CharField(max_length=20,
                                    verbose_name="分类名", )
    # 分类简介
    classifyabstract = models.TextField(verbose_name="分类简介", null=True, blank=True)

    def __str__(self):
        return self.classifyname

    class Meta:
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name


# 商品SKU表
class GoodsSKU(BaseModel):
    # 商品名
    goodsname = models.CharField(max_length=50,
                                 verbose_name="商品名称",
                                 )
    # 商品简介
    goodsabstract = models.CharField(max_length=100,
                                     verbose_name="商品简介", null=True, blank=True)

    goodprice = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="商品价格", default=0)
    # 商品单位
    goodsunit = models.ForeignKey(verbose_name="商品单位",
                                  to="Unit",
                                  blank=True,
                                  )
    goodsstock = models.IntegerField(verbose_name="商品库存", default=0, blank=True, )
    goodssales = models.FloatField(verbose_name="商品销量", default=0, blank=True)

    logoaddress = models.ImageField(verbose_name="商品封面图",
                                    upload_to='goods/%Y%m/%d',
                                    blank=True
                                    )
    # 产品是否上架
    goodsshow = models.BooleanField(verbose_name="产品是否上架", default=1, blank=True)

    # 与商品分类的ID建立  多对1的联系
    goodsverboseid = models.ForeignKey(verbose_name="商品分类ID",
                                       to="GoodsClassify",
                                       )
    # 关联字段在后台的显示
    def verboseid_name(self):
        return self.goodsverboseid.classifyname
    verboseid_name.short_description = "分类名"


    # 商品SPU_id
    goodsSPUid = models.ForeignKey(verbose_name='商品SPUid', to="GoodsSPU")
    def goodspu(self):
        return self.goodsSPUid.SPUname
    goodspu.short_description = "商品SPU名称"

    def __str__(self):
        return self.goodsname

    class Meta:
        verbose_name = "商品SKU表"
        verbose_name_plural = verbose_name


# 商品SPU表
class GoodsSPU(BaseModel):
    SPUname = models.CharField(verbose_name="商品SPU名称",
                               max_length=100, blank=True, )

    SPUdetail = RichTextUploadingField(verbose_name="商品详情", blank=True)

    # SPUdetail = models.TextField(verbose_name="SPU详情", null=True,
    #                              blank=True, )

    def __str__(self):
        return self.SPUname

    class Meta:
        verbose_name = "商品SPU"
        verbose_name_plural = verbose_name


# 商品相册表
class GoodsPicture(BaseModel):
    pictureaddress = models.ImageField(verbose_name="图片地址",
                                       upload_to="goods/%Y%m/%d",
                                       null=True,
                                       blank=True,
                                       )
    goods = models.ForeignKey(verbose_name="商品ID",
                              to="GoodsSKU",
                              null=True,
                              blank=True,
                              )

    def __str__(self):
        return self.goods.goodsname

    class Meta:
        verbose_name = "商品图片"
        verbose_name_plural = verbose_name


# 商品单位表
class Unit(BaseModel):
    unitname = models.CharField(verbose_name="单位名称",
                                max_length=20,
                                )

    def __str__(self):
        return self.unitname

    class Meta:
        verbose_name = "计量单位表"
        verbose_name_plural = verbose_name


# ========================================================

# 首页轮播商品表
class FirstBroadcast(BaseModel):
    firstname = models.CharField(verbose_name="首页名称",
                                 max_length=50, null=True,
                                 blank=True,
                                 )
    goodsSku = models.IntegerField(verbose_name="商品SKUID")
    firstpicture = models.ImageField(verbose_name="图片",
                                     upload_to="goods/first/%Y%m/%d",
                                     blank=True,
                                     )
    firstorder_choices = (
        (1, "时间正序"),
        (2, "时间反序"),
    )
    firstorder = models.SmallIntegerField(verbose_name="排序方式", choices=firstorder_choices, default=1)

    def __str__(self):
        return self.firstname

    class Meta:
        db_table = "FirstBroadcast"
        verbose_name = "首页轮播商品表"
        verbose_name_plural = verbose_name


# 首页活动表
class FirstActivity(BaseModel):
    activityname = models.CharField(verbose_name="活动名称", max_length=50, null=True, blank=True)
    activitypicture = models.ImageField(verbose_name="活动图片",
                                        upload_to="goods/activity/%Y%m/%d",
                                        null=True, blank=True)
    activityurl = models.URLField(verbose_name="活动url地址", null=True, blank=True)

    def __str__(self):
        return self.activityname

    class Meta:
        db_table = "FirstActivity"
        verbose_name = "首页活动表"
        verbose_name_plural = verbose_name


# 首页活动专区表
class ActivityArea(BaseModel):
    areaname = models.CharField(verbose_name="名称", max_length=40, null=True, blank=True)
    areadescribe = models.TextField(verbose_name="活动专区描述", null=True, blank=True)
    areaoder_choices = (
        (1, "时间正序"),
        (2, "时间反序"),
    )
    areaorder = models.SmallIntegerField(verbose_name="排序方式",
                                         choices=areaoder_choices,
                                         default=1, blank=True)

    def __str__(self):
        return self.areaname

    class Meta:
        db_table = "ActivityArea"
        verbose_name = "首页活动专区表"
        verbose_name_plural = verbose_name


# 首页专区活动商品
class Activitygoods(BaseModel):
    areaadress = models.ForeignKey(to="ActivityArea",
                                   verbose_name="专区ID",
                                   )
    goodssku = models.ManyToManyField(to="GoodsSKU", verbose_name="商品SKU ID")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "Activitygoods"
        verbose_name = "首页专区活动商品"
        verbose_name_plural = verbose_name

# =============================================================

# 用户信息表使用sm_user下models创建的UserInfo表
# from sm_user.models import UserInfo

# 收获地址表
