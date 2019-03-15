from django.shortcuts import render
from django.contrib.auth.backends import ModelBackend   #导入ModelBackend
from django.contrib.auth import  get_user_model  #导入get_user_model
from django.db.models import Q   #导入Q，使用或、与用
from rest_framework.mixins import CreateModelMixin   #发送验证码类用
from rest_framework import  mixins   #导入mixins
from rest_framework import viewsets   #发送验证码类用
from rest_framework.response import Response   #导入Response
from rest_framework import status   #导入status
from random import choice   #导入choice，生成验证码用
from rest_framework_jwt.serializers import jwt_encode_handler,jwt_payload_handler   #导入 jwt_encode_handler,jwt_payload_handler ，返回token用
from rest_framework import permissions   #导入权限
from rest_framework import authentication   #导入用户认证
from rest_framework_jwt.authentication import JSONWebTokenAuthentication   #导入JSONWebTokenAuthentication，为了配置token权限

from .serializers import SmsSerializer ,UserRegSerializer,UserDetailSerializer  #导入SmsSerializer
from utils.yunpian import YunPian   #导入YunPian
from MxShop.settings import APIKEY   #导入 APIKEY
from .models import VerifyCode   #导入数据库VerfyCode

User = get_user_model()  #get_user_model() 函数直接返回User类，找的是settings.AUTH_USER_MODEL变量的值
# Create your views here.


#自定义用户登录函数，一定要继承ModelBackend，然后重写里面的authenticate函数
class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """
    def authenticate(self,username=None,password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username)|Q( mobile=username))
            if user.check_password(password):   #传递的明文密码，调用check_password，就会对password进行加密然后比较
                return user
        except Exception as e:
            return None


#发送短信验证码view
class SmsCodeViewset(CreateModelMixin,viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    #需要验证，验证放在serializers中
    serializer_class = SmsSerializer   #配置serializer_class等于SmsSerializer

    #生成code函数
    def generate_code(self):
        """
        生成四位数字的验证码
        :return:
        """
        seeds = "1234567890"   #种子
        random_str = []
        for i in range(4):   #循环四次，取随机
            random_str.append(choice(seeds))   #取随机一个数

        return "".join(random_str)   #返回由空字符串间隔列表组成的字符串


    #重写CreateModelMixin中的create方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)   #raise_exception设置为True，如果此处判断无效，会直接抛异常（返回400），不会进入后面的部分

        mobile = serializer.validated_data["mobile"]   #获取serializer验证数据中的mobile内容

        yun_pian = YunPian(APIKEY)

        code = self.generate_code()
        sms_status = yun_pian.send_sms(code=code,mobile=mobile)

        if sms_status["code"] != 0:
            return Response({
                "mobile":sms_status["msg"]
            },status=status.HTTP_400_BAD_REQUEST)    #如果code不等于0，则返回400
        else:
            code_record = VerifyCode(code=code,mobile=mobile)
            code_record.save()   #如果发送成功，将code和mobile保存到VerfyCode数据库中
            return Response({
                "mobile":mobile
            },status=status.HTTP_201_CREATED)   #201表示请求成功

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


#用户注册
class UserViewset(CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):   #put是更新操作，patch是部分更新
    """
    用户
    """
    serializer_class = UserRegSerializer   #定义serializer类为UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (authentication.SessionAuthentication,JSONWebTokenAuthentication)   #用户认证配置,配置用户session ,以便于用浏览器调试方便，用文档测试也可以
                                                        #jwttoken也配置进用户认证中

    #重写 get_serializer_class函数，动态获取serializer
    def get_serializer_class(self):
        if self.action == "retrieve":    #使用了Viewset，才能使用self.action.使用APiView没有这个功能 #获取详细信息的时候
            return UserDetailSerializer   #如果是retrieve请求，就返回UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer   #如果是create请求，就返UserRegSerializer

        return UserDetailSerializer    #其他情况默认返回UserDetailSerializer。这行代码一定要加，否则会报错




    # permission_classes = (permissions.IsAuthenticated,)   #权限设置,保证访问必须是在用户登录的情况下

    #重写get_permissions函数，动态处理权限问题，动态设置permissions
    def get_permissions(self):
        if self.action == "retrieve":    #使用了Viewset，才能使用self.action.使用APiView没有这个功能
            return [permissions.IsAuthenticated()]   #如果是retrieve请求，就返回权限实例为需要登录
        elif self.action == "create":
            return []   #如果是create请求，就返回空的实例

        return []   #其他情况返回一个默认值：空。这行代码一定要加，否则会报错



    #重写CreateModelMixin中的create方法，用户注册
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)   #raise_exception设置为True，如果此处判断无效，会直接抛异常（返回400），不会进入后面的部分
        user = self.perform_create(serializer)

        #定制化token和name
        re_dict = serializer.data   #取出serializer的data
        payload = jwt_payload_handler(user)   #重写payload ,传递一个user
        re_dict["token"] = jwt_encode_handler(payload)   #将re_dict中的token赋值jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username   #如果user中有name,则将user模块中name值赋值给re_dict中的"name"
                                                                        #否则就将user模块中的username值赋值给re_dict中的"name"

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)   #返回re_dict的值，完成一个token的定制化

    #c重写get_object方法(此方法会在mixins.RetrieveModelMixin中用到),返回user,即返回用户
    def get_object(self):
        return self.request.user   #随意传递一个数值进来，返回的都是当前的用户

    #重载perform_create，此原函数只是调用了 serializer.save()，但是没有返回值，此处需要返回值，所以需要重写
    def perform_create(self, serializer):
        return  serializer.save()    #返回serializer的models对象