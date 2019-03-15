from datetime import datetime

from django.db import models
from django.contrib.auth import  get_user_model  #导入get_user_model

from goods.models import Goods
User = get_user_model()  #get_user_model() 函数直接返回User类，找的是settings.AUTH_USER_MODEL变量的值
# Create your models here.


class UserFav(models.Model):
    """
    用户收藏
    """
    user = models.ForeignKey(User, verbose_name=u"用户", on_delete=models.PROTECT)
    goods = models.ForeignKey(Goods, verbose_name=u"商品", on_delete=models.PROTECT,help_text="商品id")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户收藏"
        verbose_name_plural = verbose_name
        unique_together = ("user","goods")  #unique_together中设置的字段作为联合唯一索引。不会出现这里设置的字段联合起来会有两条数据的情况
                            #此处设置"user"和"goods"组成联合唯一，如果出现重复，数据库会进行处理，抛出异常
                            #设置完成后，一定要makemigrations和migrate,但设置之前要先将该表清空，因为如果表里有重复数据会migrate失败

    def __str__(self):
        # return self.user.name    #user.name有可能为None，所以会报错，此处返回一个username，就不会出错了
        return self.user.username


class UserLeavingMessage(models.Model):
    """
    用户留言
    """
    MESSAGE_CHOICES = (
        (1, "留言"),
        (2, "投诉"),
        (3, "询问"),
        (4, "售后"),
        (5, "求购")
    )
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.PROTECT)
    message_type = models.IntegerField(default=1, choices=MESSAGE_CHOICES, verbose_name="留言类型",
                                      help_text=u"留言类型: 1(留言),2(投诉),3(询问),4(售后),5(求购)")
    subject = models.CharField(max_length=100, default="subject", verbose_name="主题")
    message = models.TextField(default="default", verbose_name="留言内容", help_text="留言内容")
    file = models.FileField(upload_to="message/images/", verbose_name="上传的文件", help_text="上传的文件")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户留言"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.subject

class UserAddress(models.Model):
    """
    用户收货地址
    """
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.PROTECT)
    province = models.CharField(max_length=100, default="default", verbose_name="省份")
    city = models.CharField(max_length=100, default="default", verbose_name="城市")
    district = models.CharField(max_length=100, default="default", verbose_name="区域")
    address = models.CharField(max_length=100, default="default", verbose_name="详细地址")
    signer_name = models.CharField(max_length=100, default="default", verbose_name="签收人")
    signer_mobile = models.CharField(max_length=11, default="default", verbose_name="电话")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "收货地址"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.address
