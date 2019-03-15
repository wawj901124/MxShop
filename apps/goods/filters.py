import django_filters   #导入django_filters
from django.db.models import Q   #导入Q   ，可使用或，与运算符

from .models import Goods



class GoodsFilter(django_filters.rest_framework.FilterSet):  #继承django_filters.rest_framework.FilterSet
    """
    商品的过滤类
    """
    pricemin = django_filters.NumberFilter(name="shop_price",help_text="最低价格" , lookup_expr='gte')   #name规定检索的字段，lookup_expr规定操作的类型,gte表示大于等于
    pricemax = django_filters.NumberFilter(name="shop_price", lookup_expr='lte') #lte表示小于等于
    name = django_filters.CharFilter(name='name',lookup_expr='icontains')  #lookup_expr='icontains'表示操作的类型为“contains”，前面的i表示忽略大小写
                                                                            #配置name为模糊搜索
    # name = django_filters.CharFilter(name='name')  #不指定lookup_expr，就是全部匹配
    top_category = django_filters.NumberFilter(method='top_category_filter')    #外键的过滤要用NumberFilter，外键实际是个Number
                                                            #method,可以自己传递一个函数进来,可以自定义过滤的函数

    #自定义查找第一类别的所有商品
    def top_category_filter(self,queryset,name,value): #queryset,name,value这三个参数会默认传递进来，需要将参数写进来
        queryset = queryset.filter(Q(category_id = value)| Q(category__parent_category_id = value)| Q(category__parent_category__parent_category_id = value))
                        #category_id等于传进来的value 或者 category的父的category_id等于传进来的value或者category的父的category的父的category_id等于传进来的value
        return queryset   #返回queryset


    class Meta:
        model = Goods   #指定模型
        fields = ['pricemin', 'pricemax','name','is_hot','is_new']   #指定字段
                                #添加“is_hot”字段来过滤是否热销商品

