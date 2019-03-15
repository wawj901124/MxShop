from rest_framework import viewsets   #导入viewsets
from rest_framework import mixins   #导入mixins
from rest_framework.permissions import IsAuthenticated   #导入IsAuthenticated，判断用户是否登录
from rest_framework_jwt.authentication import JSONWebTokenAuthentication   #导入JSONWebTokenAuthentication，为了配置token权限
from rest_framework.authentication import SessionAuthentication   #导入SessionAuthentication   ，加sessiontoken的权限

from .models import UserFav,UserLeavingMessage,UserAddress   #导入UserFav
from .serializers import UserFavSerializer,UserFavDetailSerializer,LeavingMessageSerializer,AddressSerializser   #导入UserFavSerializer
from utils.permissions import IsOwnerOrReadOnly   #导入IsOwnerOrReadOnly
# Create your views here.


class UserFavViewset(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet) :   #用户收藏Viewset
                    #收藏，就是添加一条数据；取消收藏，就是删除一条数据
                    #mixins.CreateModelMixin:新加数据；mixins.DestroyModelMixin：删除数据；
                    #mixins.ListModelMixin：收藏列表功能
    """
    list:
        获取用户收藏列表
    retrieve:
        判断某个商户是否已经收藏
    create:
        收藏商品
    """
    # queryset = UserFav.objects.all()
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)   #配置权限class，IsAuthenticate验证是否登录，IsOwnerOrReadOnly验证删除时是否是本用户删除本用户数据
    # serializer_class = UserFavSerializer   #静态设置serializer_class
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)   #配置用户权限验证，配置token验证
                                #配置sessiontoken权限后，才能登录成功，否则获取不到登录信息
    lookup_field = 'goods_id'   #搜索字段配置，是否是根据这个goods_id找的，设置使用goods_id来查找，就不能使用id查找了
                                 #自己设置搜索哪个字段

    # #重载perform_create，在CreateModelMixin中
    # def perform_create(self, serializer):
    #     instance = serializer.save()     #instance是UserFav对象的序列化
    #     goods = instance.goods   #当用户创建收藏的时候，找到相应的商品（goods）,然后将其收藏数加1
    #                             #goods是UserFav Model中的goods字段
    #     goods.fav_num +=1   #收藏数加1
    #     goods.save()   #保存


    #重载get_queryset,保证获取到的数据是当前用户的数据
    def get_queryset(self):
        # a = {}
        # print(a["b"])    #手工制作一个异常，看sentry是否可以捕获到异常
        return UserFav.objects.filter(user=self.request.user)   #获取到当前用户的数据

    #重写get_serializer_class函数，动态获取serializer_class
    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer    #如果是list请求，就返回收藏详情序列
        elif self.action == "create":
            return UserFavSerializer   #如果是create请求，就返回收藏序列

        return UserFavSerializer   #默认返回收藏序列


#用户留言viewset
class LeavingMessageViewset(mixins.ListModelMixin,mixins.DestroyModelMixin,mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    #mixins.ListModelMixin,列表；mixins.DestroyModelMixin，删除；mixins.CreateModelMixin，添加;viewsets.GenericViewSet,格式化一下；
    """
    list:
        获取用户留言
    create:
        添加留言
    delete:
        删除留言功能
    """
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)   #配置权限class，IsAuthenticate验证是否登录，IsOwnerOrReadOnly验证删除时是否是本用户删除本用户数据
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)   #配置用户权限验证，配置token验证
                                #配置sessiontoken权限后，才能登录成功，否则获取不到登录信息
                                #优先使用JWTtoken的方式验证
    serializer_class = LeavingMessageSerializer   #配置serializer_class

    #重载get_queryset,保证获取到的数据是当前用户的数据
    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)   #获取到当前用户的数据

#收货地址Viewset
# class AddressViewset(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,
#                      viewsets.GenericViewSet):
#     #列表，添加，更新，删除
class AddressViewset(viewsets.ModelViewSet):   #viewsets.ModelViewSet,就集合了增删改查的功能
    """
    收货地址管理
    list:
        获取收获地址
    create:
        添加收获地址
    update:
        更新收获地址
    delete:
        删除收获地址
    """
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)   #配置权限class，IsAuthenticate验证是否登录，IsOwnerOrReadOnly验证删除时是否是本用户删除本用户数据
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)   #配置用户权限验证，配置token验证
                                #配置sessiontoken权限后，才能登录成功，否则获取不到登录信息
                                #优先使用JWTtoken的方式验证
    serializer_class = AddressSerializser  #配置serializer_class

    #重载get_queryset,保证获取到的数据是当前用户的数据
    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)   #获取到当前用户的数据




