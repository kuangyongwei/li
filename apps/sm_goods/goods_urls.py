from django.conf.urls import url
from django.views.decorators.cache import cache_page

from sm_goods.views import DetailViews, CategoryView, IndexViews

urlpatterns = [
    url(r'^$', cache_page(3600 * 24)(IndexViews.as_view()), name="index"),
    # 两个参数,第一个标识分类ID,  第二个表示排序方式
    url(r'^category/(?P<cate_id>\d+)_(?P<order>\d+)/$', CategoryView.as_view(), name="category"),
    url(r'^detail/(?P<sku_id>\d+)/$', DetailViews.as_view(), name="detail"),
]

# 在路由位置给首页添加缓存,将html文件缓存到内存中,增加访问速度
# from django.views.decorators.cache import cache_page
#
# urlpatterns = [
#     path('foo/<int:code>/', cache_page(60 * 15)(my_view)),
# ]
# cache_page(3600*24)(IndexViews.as_view())
