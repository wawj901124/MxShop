from rest_framework import serializers   #导入serializers
from django.contrib.auth import  get_user_model  #导入get_user_model
import re  #导入正则表达式模块
from datetime import datetime   #导入
from datetime import timedelta   #导入
from rest_framework.validators import UniqueValidator   #导入UniqueValidator，验证是否唯一

from .models import VerifyCode   #导入VerfyCode
from MxShop.settings import REGEX_MOBILE   #导入settings中的变量REGEX_MOBILE


User = get_user_model()  #get_user_model() 函数直接返回User类，找的是settings.AUTH_USER_MODEL变量的值


#发送短信Serializer
class SmsSerializer(serializers.Serializer):
    mobile =serializers.CharField(max_length=11)

    #新建验证mobile字段函数，名字以validate开头，拼接mobile
    def validate_mobile(self, mobile):
        """
        验证手机号码
        :param data:
        :return:
        """
        #验证手机是否注册，查询用户表
        if User.objects.filter(mobile=mobile).count():   #如果存在
            raise serializers.ValidationError("用户已经存在")   #则返回用户已经存在的提示

        #验证手机号码是否合法，要用到正则表达式
        if not re.match(REGEX_MOBILE,mobile):   #如果验证不通过
            raise serializers.ValidationError("手机号码非法")  # 则返回手机号码非法的提示

        #验证发送频率，如果不限制频率，则可以一直发送，对后台会造成很大压力
        #设置发送频率为1分钟
        one_minutes_ago = datetime.now() - timedelta(hours=0,minutes=1,seconds=0)   #获取一分钟之前的时间
        if VerifyCode.objects.filter(add_time__gt=one_minutes_ago,mobile=mobile).count():
            # 如果add_time大于one_minutes_ago时间,mobile等于传递进来的mobile,如果有这么一条记录，说明已经发送过了
            raise serializers.ValidationError("距离上一次发送未超过60s")  # 则返回距离上一次发送未超过60s的提示

        return mobile   #如果验证通过，则返回mobile

#用户详情serializers
class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    class Meta:
        model = User
        fields = ("name","gender","birthday","email","mobile")   #Serializer字段


#注册serializers
class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=4,min_length=4,required=True,help_text="验证码",label="验证码",
                                     write_only=True,  #write_only=True表示在返回前端做序列化的时候就不会序列化了
                                 error_messages={    #可以设置每一种错误的提示
                                     "blank":"请输入验证码",   #表示这个字段传入空时，报相应错误
                                     "required":"请输入验证码",   #required表示连这个字段都没有时，才会报这个错误
                                     "max_length":"验证码格式错误",
                                     "min_length":"验证码格式错误",

                                 })   #最大和最小都是4个   #自定义的一个code的serializers
                                       #required=True,表示是必填字段
                                        #error_messages配置错误信息提示
    #username验证
    username = serializers.CharField(required=True,allow_blank=False,label="用户名",help_text="用户名",
                                     validators=[UniqueValidator(queryset=User.objects.all(),message="用户已经存在")])
                #validators字段的值是验证内容，UniqueValidator表示验证如果是唯一，就提示“用户已经存在”
    password = serializers.CharField(
        style={'input_type':'password'} ,  #表示字段输入设置为密文，而不是明文
        help_text="密码",
        label="密码",
        write_only=True,  # write_only=True表示在返回前端做序列化的时候就不会序列化了,密码不能返回，会被截获，造成安全问题
    )

    # #重载create方法，加一些判断,加了set_password的逻辑
    # def create(self, validated_data):
    #     user = super(UserRegSerializer,self).create(validated_data=validated_data)   #掉用user 的 super方法
    #     user.set_password(validated_data["password"])   #设置密码，使密码加密
    #     user.save()   #保存
    #     return user   #返回user

    #验证验证码
    def validate_code(self, code):
    #     try:
    #         verify_records = VerfyCode.objects.get(mobile=self.initial_data["username"],code=code)
    #                 #get在两种情况下抛异常：1.获取两条以上的数据会报错；2.不存在值使会报异常
    #     except VerfyCode.DoesNotExist as e:   #不存在异常的处理
    #         pass
    #     except VerfyCode.MultipleObjectsReturned as e:   #存在两条级两条以上的处理
    #         pass
    #
    #     #或者
    #     try:
    #         verify_records = VerfyCode.objects.get(mobile=self.initial_data["username"],code=code)
    #                 #get在两种情况下抛异常：1.获取两条以上的数据会报错；2.不存在值使会报异常
    #     except Exception as e:   #所有异常的处理，一般不建议使用，不知道是哪种异常
    #         pass


        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")  #self.initial_data就是前端传递过来的数据
                                                                                            #获取到手机号是前端传过来的username的值
                                                                                            #按照添加时间倒序排序
                                                                                            #filter如果找不到会返回一个空数组，如果找到两个及以上，会返回数组
                                                                                            #使用get对过期时间也不好处理
        if verify_records:   #如果有的话，取最新一条
            last_record = verify_records[0]

            five_minutes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)  # 获取5分钟之前的时间

            #验证code是否超过5分钟
            if five_minutes_ago > last_record.add_time:   #如果five_minutes_ago大于last_record中的add_time，则表示过期
                raise serializers.ValidationError("验证码过期")   #返回验证码过期信息

            #验证code是否存在
            if last_record.code != code:   #如果last_record中的code不等于传递出来的code,则报错
                raise serializers.ValidationError("验证码错误")   #报验证码错误信息

        else:
            raise serializers.ValidationError("验证码错误")  # 报验证码错误信息，其实是验证码不存在

    #作用域所有字段之上,做全盘的设置，统一处理
    def validate(self, attrs):   #attrs是validate之后返回的总的字段
        attrs["mobile"] = attrs["username"]    #给attrs数组增加一个mobile字段，值等于username的值，不需要前端传递mobile值
        del attrs["code"]   #删除掉attrs数组中的code内容
        return attrs   #返回数组

    class Meta:
        model = User
        fields = ("username","code","mobile","password")   #code不再数据库User中，是自己添加的一个Serializer字段














