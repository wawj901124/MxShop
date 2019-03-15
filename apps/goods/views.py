from rest_framework.views import APIView   #导入APIView
from rest_framework.response import Response #导入Response，drf的Response，远比django中的Response强大
# from rest_framework import status   #导入状态码status
from rest_framework.pagination import PageNumberPagination   #导入PageNumberPagination
from rest_framework import viewsets   #viewsets，一个很重要的view
from rest_framework import  filters   #搜索过滤用
from django_filters.rest_framework import DjangoFilterBackend   #导入 DjangoFilterBackend，字段过滤用
from rest_framework.authentication import TokenAuthentication   #导入TokenAuthentication
from rest_framework_extensions.cache.mixins import CacheResponseMixin   #导入缓存机制包CacheResponseMixin
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle  #导入限速包UserRateThrottle（登录用户限速）,AnonRateThrottle （匿名用户限速）

from .models import Goods,GoodsCategory,Banner
from .serializers import GoodsSerializer,CategorySerializer,BannerSerializer,IndexCategorySerializer
from .filters import GoodsFilter


# Create your views here.


# class GoodsListView(APIView):   #继承APIView的View
#     """
#     List all goods!
#     """
#     def get(self,request,format=None):
#         goods = Goods.objects.all()[:10]   #取十个
#         goods_serializer = GoodsSerializer(goods,many =True)   #goods为列表时，一定要有many =True，如果goods只是一项时，可以不用配置many的值
#                                                         #将goods列表序列化成一个数组对象
#         return Response(goods_serializer.data)   #返回goods_serializer的data,data就是序列化后的数据
#
#     #接收前端传递的数据，然后进行保存，保存到数据库当中
#     def post(self,request,format=None):
#         serializer = GoodsSerializer(data = request.data) #data取 request中的data，而django中request是没有data的属性的
#         if serializer.is_valid():   #如果合法，保存，is_valid验证合法性，根据model中的属性来验证
#             serializer.save()  #save会调用GoodsSerializer中的create()方法
#             return Response(serializer.data,status =status.HTTP_201_CREATED)   #status是状态码，传递数据成功，返回一个201，201是post响应成功，200是get请求的一个响应
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import mixins   #导入mixins
from rest_framework import generics   #导入generics


# class GoodsListView(mixins.ListModelMixin,generics.GenericAPIView):  # 继承mixins.ListModelMixin和generics.GenericAPIView
#                                                     #generics.GenericAPIView是一个非常重要的view,也是用的相当多的view
#                                                     #mixins.CreateModelMixin可以post提交数据
#     """
#     商品列表页
#     """
#     queryset = Goods.objects.all()[:10]   #实体
#     serializer_class = GoodsSerializer   #serializer类
#
#     def get(self, request, *args, **kwargs):   #不定义的get话话，默认不接受这种请求，所有此处要重写get函数
#         return self.list(self, request, *args, **kwargs)   #调用mixins.ListModelMixin中的list函数


class GoodsPagination(PageNumberPagination):   #定制化rest framework 的分页的配置,继承PageNumberPagination
    page_size = 12  #默认显示12条
    page_size_query_param = 'page_size'   #指明向后台要多少条，指定这页有多少个
    page_query_param = 'page'   #指明访问页的参数，代表请求多少页
    max_page_size = 100   #最大的页面最大的数量只能是100个，最大可显示100条


# class GoodsListView(generics.ListAPIView):  # 继承generics的列表页的ListAPIView，减少代码量
#     """
#     商品列表页
#     """
#     # queryset = Goods.objects.all()[:10]   #实体
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer   #serializer类
#     pagination_class = GoodsPagination   #设置分页的类为定制的GoodsPagination的类 ，
#                                         # 可以代替在Settings中对REST_FRAMEWORK 的配置


class GoodsListViewSet(CacheResponseMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):  # 继承viewsets的中的GenericViewSet
                    #GenericViewSet中没有定义get和post方法（action的方法），所有又要用到mixins.ListModelMixin
                    #mixins.RetrieveModelMixin:增加商品详情页的接口
                    #CacheResponseMixin,缓存机制类，放在最前面，这个顺序比较重要，需要对那个接口进行缓存，就加到哪个ViewSet中即可
                    #个人数据建议不做缓存，像那种登录或不登录都能看到的数据建议可以做缓存
                    #使用的是内存缓存，系统重启后，缓存便没了
    """
    商品列表页,分页，搜索，过滤，排序
    """
    throttle_classes = (UserRateThrottle,AnonRateThrottle)    #用户访问限速配置
    # queryset = Goods.objects.all()[:10]   #实体
    # queryset = Goods.objects.all()
    # queryset = Goods.objects.filter(shop_price__gt = 100)  #返回大于100的商品
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer   #serializer类
    pagination_class = GoodsPagination   #设置分页的类为定制的GoodsPagination的类 ，
                                        # 可以代替在Settings中对REST_FRAMEWORK 的配置
    # authentication_classes = (TokenAuthentication,)   #登录验证类设置，等用于settings中 'rest_framework.authentication.TokenAuthentication',  #新加token验证类,验证用户信息
                                                    #只用一项的时候，一定要加逗号
                                                    #商品列表页是一个公开的页面，所以此处不同配置登录信息验证类

    #字段过滤
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)   #配置过滤：配置精准过滤，过滤的内容要完全等于输入的内容
                        #DjangoFilterBackend字段过滤，filters.SearchFilter为搜索过滤,filters.OrderingFilter为排序过滤
    # filter_fields = ('name', 'shop_price')   #配置过滤：配置过滤的字段，过滤的内容要完全等于输入的内容
    filter_class = GoodsFilter   #配置过滤，配置过滤类
    search_fields = ('name', 'goods_brief', 'goods_desc')  #配置搜索过滤,name,表示在这个name字段内容里,进行模糊搜索
    # search_fields = ('^name','goods_brief','goods_desc')   #配置搜索过滤,^name,表示在这个name字段内容里，搜索以输入内容开头的内容
    # search_fields = ('=name', 'goods_brief', 'goods_desc')  # 配置搜索过滤,=name,表示在这个字段内容里，搜索完全等于输入内容的内容
    ordering_fields = ('sold_num','shop_price')   #配置排序过滤:销量和价格

    #重载retrieve，获取商品详情用
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()   #获取实例
        instance.click_num += 1   #点击数加1
        instance.save()   #保存
        serializer = self.get_serializer(instance)   #获取序列化
        return Response(serializer.data)   #返回序列化数据

    # def get_queryset(self):
    #     queryset = Goods.objects.all()
    #     price_min = self.request.query_params.get("price_min",0)
    #     if price_min:
    #         queryset = queryset.filter(shop_price__gt = int(price_min))
    #     return queryset
    #     # return Goods.objects.filter(shop_price__gt = 100)   #返回大于100的商品


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,viewsets.GenericViewSet):
                    #mixins.RetrieveModelMixin获取某个商品的详情，不用再配置url,mixins.RetrieveModelMixin已经自动配置了url
    """
    list:
        商品分类列表数据
    retrieve:
        获取商品分类详情
    """
    # queryset = GoodsCategory.objects.all()  #获取所有类别
    queryset = GoodsCategory.objects.filter(category_type=1)  # 获取所有类别
    serializer_class = CategorySerializer  # serializer类

#轮播图
class BannerViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):  #获取列表
    """
    获取轮播图列表
    """
    queryset = Banner.objects.all().order_by("index")  # 获取所有,根据index 顺序排列
    serializer_class = BannerSerializer  # serializer类


class IndexCategoryViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True,name__in=["生鲜食品","酒水饮料"])  # 获取is_tab=True，商品名字为"生鲜食品","酒水饮料"，只是这两种的数据的所有数据
    serializer_class = IndexCategorySerializer  # serializer类











