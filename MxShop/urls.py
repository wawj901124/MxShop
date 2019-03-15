"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path,include   #导入path和include

import xadmin
from MxShop.settings import MEDIA_ROOT   #访问图片配置，导入MEDIA_ROOT
from django.views.static import serve  #访问图片配置，导入django.views.static（专门做静态文件的）中的serve
from rest_framework.documentation import include_docs_urls   #导入include_docs_urls,可以查看文档
from rest_framework.routers import DefaultRouter   #导入DefaultRouter，使用routers，让url配置更简单
from rest_framework.authtoken import views   #配置token路径 2-1,导入authtoken的views
from rest_framework_jwt.views import obtain_jwt_token   #配置jwt路径 2-1导入jwt

# from goods.views_base import GoodsListView   #导入GoodsListView
# from goods.views import GoodsListView   #导入GoodsListView
from goods.views import GoodsListViewSet,CategoryViewSet,BannerViewSet,IndexCategoryViewSet   #导入GoodsListViewSet
from users.views import SmsCodeViewset,UserViewset   #导入SmsCodeViewset
from user_operation.views import UserFavViewset,LeavingMessageViewset,AddressViewset   #导入UserFavViewset
from trade.views import ShoppingCartViewset,OrderViewset   #导入 ShoppingCartViewset


router = DefaultRouter()   #实例化

#配置goods的url
router.register('goods', GoodsListViewSet,base_name='goods')  #将goods注册到router中，后期大部分的url都会基于这个来配置
            #router已经自动绑定post请求到create方法中，自动绑定get请求到list方法中

#配置category的url
router.register('categorys', CategoryViewSet,base_name='categorys')  #将categorys注册到router中，后期大部分的url都会基于这个来配置
            #router已经自动绑定post请求到create方法中，自动绑定get请求到list方法中

router.register('codes', SmsCodeViewset,base_name='codes')  #配置验证码的url
            #router已经自动绑定post请求到create方法中，自动绑定get请求到list方法中

router.register('users', UserViewset,base_name='users')  #配置用户注册接口的url
            #router已经自动绑定post请求到create方法中，自动绑定get请求到list方法中

#收藏
router.register(r'userfavs',UserFavViewset,base_name="userfavs")

#留言
router.register(r'messages',LeavingMessageViewset,base_name="messages")

#收货地址
router.register(r'address',AddressViewset,base_name="address")

#购物车url配置
router.register(r'shopcarts',ShoppingCartViewset,base_name="shopcarts")

#订单相关url配置
router.register(r'orders',OrderViewset,base_name="orders")

#轮播图相关url配置
router.register(r'banners',BannerViewSet,base_name="banner")

#首页商品系列数据相关url配置
router.register(r'indexgoods',IndexCategoryViewSet,base_name="indexgoods")

# goods_list = GoodsListViewSet.as_view({   #自己设置绑定
#     'get': 'list',   #把get请求绑定到list方法上，作用等同于与GoodsListView中get方法中调用self.list
#     # 'post': 'create' ,  #把post请求绑定到create方法上
# })

from django.views.generic import TemplateView   #导入TemplateView ，为index.html配置路径

from trade.views import AlipayView   #导入alipay支付接口的View
urlpatterns = [
    path('xadmin/', xadmin.site.urls),
#   url(r'^media/(?P<path>.*)$',serve,{"document_root":MEDIA_ROOT}),
    path('media/<path:path>',serve,{"document_root":MEDIA_ROOT}), #访问图片配置，url配置
    path('api-auth/',include('rest_framework.urls',namespace = 'rest_framework')), #drf登录的配置

    #配置index.html路径
    path('index/',TemplateView.as_view(template_name="index.html"),name="index"),

    #商品列表页
    # path('goods/',GoodsListView.as_view(), name = "goods-list"),   #商品列表视图url,名字为goods-list
    # path('goods/',goods_list, name = "goods-list"),   #商品列表视图url,名字为goods-list
    path( '',include(router.urls)),   #配置router路径

    path('docs/', include_docs_urls(title="慕学生鲜")),  # include_docs_urls路径配置

    #获取token的url   #drf自带的token认证模式
    path('api-token-auth/', views.obtain_auth_token),  #配置token路径，2-2，配置url

    #jwt的认证接口
    path('login$/',obtain_jwt_token),   #配置jwt 2-2 配置路径,在login/后加“$”,避免与第三方登录url中的login冲突

    # alipay支付接口url配置
    path('alipay/return/', AlipayView.as_view(), name="alipay"),  #alipay支付路径

    # 第三方登录url
    path('', include('social_django.urls',namespace='social') ),  # alipay支付路径
]
