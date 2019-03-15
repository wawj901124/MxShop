from datetime import datetime

from django.db import models
from django.contrib.auth import  get_user_model  #导入get_user_model

# from users.models import UserProfile   #导入UserProfile
from goods.models import Goods

User = get_user_model()  #get_user_model() 函数直接返回User类，找的是settings.AUTH_USER_MODEL变量的值
# Create your models here.


class ShoppingCart(models.Model):
    """
    购物车
    # on_delete有CASCADE、PROTECT、SET_NULL、SET_DEFAULT、SET()五个可选择的值
    #     CASCADE：此值设置，是级联删除。
    #     PROTECT：此值设置，是会报完整性错误。
    #     EST_NULL：此值设置，会把外键设置为null，前提是允许为null。
    #     SET_DEFAULT：此值设置，会把设置为外键的默认值。
    #     SET()：此值设置，会调用外面的值，可以是一个函数。
    """
    # user = models.ForeignKey(UserProfile)
    user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.PROTECT)
    goods = models.ForeignKey(Goods, verbose_name=u"商品", on_delete=models.PROTECT)
    nums = models.IntegerField(default=0, verbose_name="购买数量")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s(%d)".format(self.goods.name, self.nums)


class OrderInfo(models.Model):
    """
    订单
    """
    ORDER_STATUS = (
        ("TRADE_SUCCESS", "成功"),
        ("TRADE_CLOSED", "超时关闭"),
        ("WAIT_BUYER_PAY", "交易创建"),
        ("TRADE_FINISHED", "交易结束"),
        ("paying", "待支付"),
    )

    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.PROTECT)
    order_sn = models.CharField(max_length=30,default="ordersn", null=True,blank=True,unique=True, verbose_name="订单号") #unique=True表示是唯一的编码
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name=u"交易号")
    pay_status = models.CharField(choices=ORDER_STATUS, default="paying", max_length=30, verbose_name="订单状态")
    post_script = models.CharField(max_length=200, verbose_name="订单留言")
    order_amount = models.FloatField(default=0.0, verbose_name="订单金额")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")

    # 用户信息
    address = models.CharField(max_length=100, default="", verbose_name="收货地址")
    signer_name = models.CharField(max_length=20, default="", verbose_name="签收人")
    singer_mobile = models.CharField(max_length=11, verbose_name="联系电话")

    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = u"订单"
        verbose_name_plural = verbose_name

    # def __str__(self):
    #     return str(self.order_sn)


class OrderGoods(models.Model):
    """
    订单的商品详情
    """
    order = models.ForeignKey(OrderInfo, verbose_name="订单信息", related_name="goods",on_delete=models.PROTECT)  #related_name="goods"
    goods = models.ForeignKey(Goods, verbose_name="商品", on_delete=models.PROTECT)
    goods_num = models.IntegerField(default=0, verbose_name="商品数量")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "订单商品"
        verbose_name_plural = verbose_name

    # def __str__(self):
    #     return str(self.order.order_sn)



