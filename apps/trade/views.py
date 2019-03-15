import time
from rest_framework import viewsets   #导入viewsets
from rest_framework.permissions import IsAuthenticated   #导入用户验证IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication   #导入JWTtoken验证
from rest_framework.authentication import SessionAuthentication   #导入session验证
from rest_framework import mixins   #导入mixins
from django.shortcuts import redirect  # 导入redirect

from utils.permissions import IsOwnerOrReadOnly   #删除的时候必须要有之前写的IsOwnerOrReadOnly
from .serializers import ShopCartSerializer,ShopCartDetatilSerializer,OrderSerializer,OrderDetailSerializer   #导入序列
from .models import ShoppingCart,OrderInfo,OrderGoods


# Create your views here.
#购物车viewset
class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create:
        加入购物车
    delete:
        删除购物记录
    read:
        获取购物车某个商品的购物详情
    """
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)   #配置权限class，IsAuthenticate验证是否登录，IsOwnerOrReadOnly验证删除时是否是本用户删除本用户数据
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)   #配置用户权限验证，配置token验证
                                #配置sessiontoken权限后，才能登录成功，否则获取不到登录信息
                                #优先使用JWTtoken的方式验证
    # serializer_class = ShopCartSerializer  #配置serializer_class
    # queryset = ShoppingCart.objects.all()   #ModelSerializer不用指明queryset，但是Serializer一定要指明queryset,此处特别容易被忽略掉
    lookup_field = 'goods_id'   #搜索字段配置，是否是根据这个goods_id找的，设置使用goods_id来查找，就不能使用id查找了
                                 #自己设置搜索哪个字段

    #重载perform_create方法，在创建时加入某些逻辑，此处对商品库存数进行修改
    def perform_create(self, serializer):
        shop_cart = serializer.save()
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums   #商品的库存数减等于购物数
        goods.save()   #保存

    #重载perform_destroy方法，在删除时加入某些逻辑，此处对商品库存数进行修改，删除时，要先处理逻辑，再删除
    def perform_destroy(self, instance):
        goods = instance.goods   #取goods是在删除前取
        goods.goods_num += instance.nums   #商品的库存数加等于购物数
        goods.save()   #保存
        instance.delete()   #删除

    #重载perform_update，在更新时加入某些逻辑，此处对商品库存数进行修改，更新时，有可能加，有可能减，所以需要保存更新前的数据，然后做一个比对
    def perform_update(self, serializer):
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)   #获取更新前商品的数据，获取到已有值,要使用serializer.instance.id，不能直接使用serializer.id
        existed_nums = existed_record.nums   #获取更新前的购物数
        save_record = serializer.save()   #获取到更新后的数值
        nums = save_record.nums - existed_nums   #更新后购物车中的购物数减去更新前购物车中的购物数，即为更新的数量
        goods = save_record.goods   #获取更新后的商品
        goods.goods_num -= nums  #库存数减等于nums（更新的数量）
        goods.save()   #保存


    #重写get_serializer_class，动态配置serializer
    def get_serializer_class(self):
        if self.action == "list":   #如果是list请求，则返回ShopCartDetatilSerializer
            return ShopCartDetatilSerializer
        else:
            return ShopCartSerializer   #否则返回ShopCartSerializer

    #重写get_queryset方法，只返回当前用户的列表
    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


#订单Viewset
class OrderViewset(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.DestroyModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):   #订单不允许修改，所有没有mixins,只有viewsets.GenericViewSet
    """
    订单管理
    list:
        获取个人订单
    delete:
        删除订单
    create:
        新增订单
    """
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)   #配置权限class，IsAuthenticate验证是否登录，IsOwnerOrReadOnly验证删除时是否是本用户删除本用户数据
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)   #配置用户权限验证，配置token验证
                                #配置sessiontoken权限后，才能登录成功，否则获取不到登录信息
                                #优先使用JWTtoken的方式验证
    serializer_class = OrderSerializer  #配置serializer_class

    #重写get_serializer_class，动态配置serializer
    def get_serializer_class(self):
        if self.action == "retrieve":   #如果是retrieve请求，则返回OrderDetailSerializer
            return OrderDetailSerializer
        else:
            return OrderSerializer   #否则返回OrderSerializer

    #重写get_queryset方法，只返回当前用户的列表
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    #重写perform_create方法,可以进行序列保存重写，而不影响mixins.CreateModelMixin中的其他的方法
    def perform_create(self, serializer):
        #保存之前要进行订单号生成，已经在序列中写了相应保存的程序
        order = serializer.save()   #默认调用保存序列
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)   #获取当前用户购物车中的数据

        #遍历循环shop_carts
        for shop_cart in shop_carts:
            order_goods = OrderGoods()   #实例化
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()   #保存到数据库中

            shop_cart.delete()   #删除数据库中对应的数据
        return order   #返回order


#alipay支付接口
from rest_framework.views import APIView   #导入APIView （最底层的iew）
from utils.alipay import AliPay   #导入AliPay
from MxShop.settings import ali_pub_key_path,private_key_path   #导入密钥路径配置
from datetime import datetime
from rest_framework.response import Response
class AlipayView(APIView):
    def get(self,request):
        """
        处理支付宝的return_url返回
        :param request:
        :return:
        """
        processed_dict = {}   #新建一个字典
        for key,value in request.GET.items():
            processed_dict[key] = value   #将 request中POST请求中数据放到processed_dict字典中

        sign = processed_dict.pop("sign",None)   #将processed_dict中的sign删除

        alipay = AliPay(
            appid="2016080600180695",
            app_notify_url="http://127.0.0.1:9000/alipay/return/",
            app_private_key_path= private_key_path,  # 应用私钥的路径
            alipay_public_key_path= ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:9000/alipay/return/"
        )

        verify_re = alipay.verify(processed_dict,sign)   #验证是否是支付宝请求过来的数据，验证支付是否有效

        if verify_re is True:  #如果是True就进行处理，如果不是就认为是恶意攻击，不进行处理
            order_sn = processed_dict.get('out_trade_no',None)   #获取processed_dict中的out_trade_no值
            trade_no = processed_dict.get('trade_no',None)
            trade_status = processed_dict.get('trade_status',None)

            #对商品的售卖数量进行修改
            existed_orders = OrderInfo.objects.filter(order_sn = order_sn)   #获取订单
            for existed_order in existed_orders:
                order_goods = existed_order.goods.all()   #反向去用related_name即可，goods为反向取的related_name
                for order_good in order_goods:
                    goods = order_good.goods   #获取goods
                    goods.sold_num += order_good.goods_num  #商品的售卖量加等于 订单里的商品数量
                    goods.save()   #保存 #对商品的售卖数量进行修改

                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()   #保存


            response = redirect("index")   #跳转到index路径
            response.set_cookie("nextPath","pay",max_age=2)  #跳转到Vue中的pay页面，max_age设置为2秒 ，
                                                    # max_age尽量设置时间短点，保证使用一次就过期
                                                    # 在cookie中 添加nextPath,值为pay
                                                    #设置cookie
            return response  #返回
        else:#如果验证不通过，则直接返回，跳转到index路径
            response = redirect("index")   #跳转到index路径
            return response  # 返回


        # return Response("success")   #返回一个success给支付宝，如果不返回success给支付宝，支付宝会不停的向这个接口发消息
                                        #但是一旦返回一个success给支付宝，支付宝就认为成功，不会再发请求了

    def post(self,request):
        """
        处理支付宝的notify_url
        :param request:
        :return:
        """
        processed_dict = {}   #新建一个字典
        for key,value in request.POST.items():
            processed_dict[key] = value   #将 request中POST请求中数据放到processed_dict字典中

        sign = processed_dict.pop("sign",None)   #将processed_dict中的sign删除

        alipay = AliPay(
            appid="2016080600180695",
            app_notify_url="http://127.0.0.1:9000/alipay/return/",
            app_private_key_path= private_key_path,  # 应用私钥的路径
            alipay_public_key_path= ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:9000/alipay/return/"
        )

        verify_re = alipay.verify(processed_dict,sign)   #验证是否是支付宝请求过来的数据，验证支付是否有效

        if verify_re is True:  #如果是True就进行处理，如果不是就认为是恶意攻击，不进行处理
            order_sn = processed_dict.get('out_trade_no',None)   #获取processed_dict中的out_trade_no值
            trade_no = processed_dict.get('trade_no',None)
            trade_status = processed_dict.get('trade_status',None)

        existed_orders = OrderInfo.objects.filter(order_sn = order_sn)   #获取订单
        for existed_order in existed_orders:
            existed_order.pay_status = trade_status
            existed_order.trade_no = trade_no
            existed_order.pay_time = datetime.now()
            existed_order.save()   #保存

        return Response("success")   #返回一个success给支付宝，如果不返回success给支付宝，支付宝会不停的向这个接口发消息
                                        #但是一旦返回一个success给支付宝，支付宝就认为成功，不会再发请求了
