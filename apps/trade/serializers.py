import time
from rest_framework import serializers   #导入serializers

from goods.models import Goods   #导入Goods
from .models import ShoppingCart,OrderInfo,OrderGoods   #导入 ShoppingCart
from goods.serializers import GoodsSerializer
from utils.alipay import AliPay   #导入 AliPay
from MxShop.settings import private_key_path,ali_pub_key_path,appid,app_notify_url,return_url #导入两个key

#购物车详情Serializer
class ShopCartDetatilSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)   #内嵌goods的Serializer,many=False表示一个ShopCart只能对应一个goods
    class Meta:
        model = ShoppingCart
        fields = "__all__"   #返回全部字段


#购物车Serializer
class ShopCartSerializer(serializers.Serializer):   #使用serializers.Serializer比serializers.ModelSerializer更灵活些
                #不使用ModelSerializer，就需要自己定义Serializer
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )    #设置user为当前用户
    # add_time = serializers.DateTimeField(read_only=True,format="%Y-%m-%d %H:%M")   #read_only=True,表示这个字段只返回不提交
    #                         #format="%Y-%m-%d %H:%M"，表示格式化时间显示
    nums = serializers.IntegerField(required=True,min_value=1,label="数量",help_text="购物数量",   #label="数量"表示说明
                                    error_messages={
                                        "min_value":"商品数量不能小于1",   #如果不满足大于等于1的条件，就提示商品数量不能小于1
                                        "required":"请选择购买数量",   #如果没有填写，则提示请选择购买数量
                                    }
                                    )   #必填，最小数量为1，定义一些错误显示
    goods = serializers.PrimaryKeyRelatedField(required=True,queryset=Goods.objects.all())   #goods是个外键，
                #ModelSerializer不用指明queryset，但是Serializer一定要指明queryset

    #继承serializers.Serializer，就必须重写create方法，因为它本身并没有提供一个save功能
    def create(self, validated_data):
        user = self.context["request"].user    #获取当前用户，在Serializer中不能直接使用self.request,而是要使用self.context["request"]
        nums = validated_data["nums"]   #获取nums
        goods = validated_data["goods"]   #获取goods对象，goods为外键

        existed = ShoppingCart.objects.filter(user=user,goods=goods)  #查看是否存在这条记录
        if existed:   #如果存在
            existed = existed[0]
            existed.nums += nums
            existed.save()   #保存
        else:
            existed = ShoppingCart.objects.create(**validated_data)   #否则就用create方法新加一个数据

        return existed   #返回记录

    # 继承serializers.Serializer，就必须重写update方法，因为它本身并没有此功能，而serializers.ModelSerializer已经写好了
    def update(self, instance, validated_data):
        #修改商品数量
        instance.nums = validated_data["nums"]   #instance实际是ShoppingCart的实例
        instance.save()   #保存
        return instance


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)   #外键，设置many=False
    class Meta:
        model = OrderGoods
        fields = "__all__"

class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)   #外键，设置many=True
    alipay_url = serializers.SerializerMethodField(read_only=True)   #使用serializers.SerializerMethodField可以在serializers中自定义添加字段
                                #此处添加一个alipay_url字段

    #序列化时生成支付宝的url
    def get_alipay_url(self,obj):   #使用get加字段名，会自动成为字段对应的函数，系统自动查找字段的函数，就是使用get_字段名
                                    #obj指OrderSerializer实例
        alipay = AliPay(
            appid=appid,
            app_notify_url=app_notify_url,
            app_private_key_path=private_key_path,  # 应用私钥的路径
            alipay_public_key_path=ali_pub_key_path,# 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,  测试环境设置为True，上线时要设置为False
            return_url=return_url
        )
        # 生成整个请求的字符串，只是字符串，要把生成的字符串放到re_url中
        url = alipay.direct_pay(  # 阿里pay的直接支付接口
            subject=obj.order_sn,   #使用order_sn作为subject
            out_trade_no=obj.order_sn,  # 我们平台的订单号
            total_amount=obj.order_amount,   #支付金额
            return_url=return_url
            # 支付完成后，要跳到自己服务的一个页面：就要使用return_url
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(
            data=url)  # alipaydev为阿里pay的沙箱环境

        print(re_url)
        return re_url   #返回re_url
    class Meta:
        model = OrderInfo
        fields = "__all__"



#订单序列
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )    #设置user为当前用户,为隐藏字段，即不显示

    pay_status = serializers.CharField(read_only=True)   #设置订单状态字段为只能读，不能写
    trade_no = serializers.CharField(read_only=True)   #设置交易号字段为只能读，不能写
    order_sn = serializers.CharField(read_only=True)   #设置订单号字段为只能读，不能写
    pay_time = serializers.DateTimeField(read_only=True,format="%Y-%m-%d %H:%M:%S")   #设置支付时间字段为只能读，不能写
    add_time = serializers.DateTimeField(read_only=True,format="%Y-%m-%d %H:%M:%S")   #read_only=True,表示这个字段只返回不提交
                            #format="%Y-%m-%d %H:%M"，表示格式化时间显示   #设置添加时间字段为只能读，不能写
    alipay_url = serializers.SerializerMethodField(read_only=True)   #使用serializers.SerializerMethodField可以在serializers中自定义添加字段
                                #此处添加一个alipay_url字段

    #序列化时生成支付宝的url
    def get_alipay_url(self,obj):   #使用get加字段名，会自动成为字段对应的函数，系统自动查找字段的函数，就是使用get_字段名
                                    #obj指OrderSerializer实例
        alipay = AliPay(
            appid=appid,
            app_notify_url=app_notify_url,
            app_private_key_path=private_key_path,  # 应用私钥的路径
            alipay_public_key_path=ali_pub_key_path,# 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,  测试环境设置为True，上线时要设置为False
            return_url=return_url
        )
        # 生成整个请求的字符串，只是字符串，要把生成的字符串放到re_url中
        url = alipay.direct_pay(  # 阿里pay的直接支付接口
            subject=obj.order_sn,   #使用order_sn作为subject
            out_trade_no=obj.order_sn,  # 我们平台的订单号
            total_amount=obj.order_amount,   #支付金额
            return_url=return_url
            # 支付完成后，要跳到自己服务的一个页面：就要使用return_url
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(
            data=url)  # alipaydev为阿里pay的沙箱环境

        print(re_url)
        return re_url   #返回re_url



    #订单号生成
    def generate_order_sn(self):
        from random import Random
        random_ins = Random()   #实例化

        #当前时间+userid+随机数
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random_ins.randint(10,99))
        #time.strftime("%Y%m%d%H%M%S")是获取当前时间，并将时间格式化为字符串形式
        #random_ins.randint(10,99)是获取10到99之间任意一个两位数

        return order_sn

    #重写validate，在validate保存order_sn后，serializer.save()  就可以直接保存了
    def validate(self, attrs):
        attrs["order_sn"] = self.generate_order_sn()   #生成并保存order_sn
        return attrs   #返回attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"



