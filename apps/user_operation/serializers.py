from rest_framework import serializers   #导入serializers
from rest_framework.validators import UniqueTogetherValidator   #导入 UniqueTogetherValidator

from .models import UserFav   #导入 UserFav
from .models import UserLeavingMessage,UserAddress   #导入UserLeavingMessage
from goods.serializers import GoodsSerializer   #导入GoodsSerializer，用户做嵌套


#用户显示Serializer
class UserFavDetailSerializer(serializers.ModelSerializer):
    # goods = GoodsSerializer(many=True)   #设置goods嵌套序列
    goods = GoodsSerializer()  # 设置goods嵌套序列，goods是个外键，不是对应多个，而是对应一个实例
    class Meta:
        model = UserFav   #model为UserFav
        fields = ("goods", "id")    #设置fields



#用户收藏Serializer
class UserFavSerializer(serializers.ModelSerializer):   #收藏的Serializer ,ModelSerializer可以认识识别Model中设置的联合唯一索引设置
                                                        #在model中配置之后，在ModelSerializer中可以不用再次配置
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )    #设置user为当前用户
    class Meta:
        model = UserFav   #model为UserFav

        validators = [   #UniqueTogetherValidator需要写在Meta信息中，因为联合索引是作用在多个字段上的，所以就不能写在某个字段上了，而要写在Meta信息中
                        #validators可以写在某个字段之上，也可以写在Meta中
            UniqueTogetherValidator(
                queryset= UserFav.objects.all(),
                fields = ("user","goods"),
                message= "已经收藏"   #添加message为"已经收藏"，message可以自己定义的一个消息内容“已经收藏” ，比数据库配置联合索引好的一点
            )
        ]   #设置联合索引唯一，  在ModelSerializer中设置联合索引唯一

        fields = ("user","goods","id")   #Serializer如果要添加删除功能，则必须要返回“id”字段
                                            #收藏记录的id,有了id后，完成删除功能就比较简单了

#留言serializer
class LeavingMessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )    #设置user为当前用户
    add_time = serializers.DateTimeField(read_only=True,format="%Y-%m-%d %H:%M")   #read_only=True,表示这个字段只返回不提交
                            #format="%Y-%m-%d %H:%M"，表示格式化时间显示
    class Meta:
        model = UserLeavingMessage   #model为UserFav
        fields = ("user", "message_type", "subject","message","file","id","add_time")

#收获地址serializer
class AddressSerializser(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )    #设置user为当前用户
    add_time = serializers.DateTimeField(read_only=True,format="%Y-%m-%d %H:%M")   #read_only=True,表示这个字段只返回不提交
                            #format="%Y-%m-%d %H:%M"，表示格式化时间显示
    class Meta:
        model = UserAddress   #model为UserAddress
        fields = ("id","user", "province", "city","district","address","signer_name","signer_mobile","add_time")


