from rest_framework import serializers   #导入serializers
from django.db.models import Q   #导入Q   ，可使用或，与运算符

from goods.models import Goods,GoodsCategory,GoodsImage,Banner,GoodsCategoryBrand,IndexAd   #导入goods

# class GoodsSerializer(serializers.Serializer):   #继承serializers中的Serializer类的goods的serializers，可以自己写所有的字段，映射model中的所有字段，与form功能相似，但是是专门用于json的
#                                                 #自定义自己的serializer,继承drf的Serializer类
#     name = serializers.CharField(max_length=100,required=True)   #required=True,是否必须，必须
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()   #drf的serializers可以把图片的路径加上meida的路径
#
#     def create(self, validated_data):   #创建goods模型的对象
#         """
#         :param validated_data:
#         :return:
#         """
#         return Goods.objects.create(**validated_data)   #object的create函数可以把前端传递的数据进行验证


class CategorySerializer3(serializers.ModelSerializer):  #创建Category的Serializer
    """
    商品类别序列化-类别三
    """
    class Meta:
        model = GoodsCategory
        fields = "__all__"



class CategorySerializer2(serializers.ModelSerializer):  #创建Category的Serializer
    """
    商品类别序列化-类别二
    """
    sub_cat = CategorySerializer3(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):  #创建Category的Serializer
    """
    商品类别序列化-类别一
    """
    sub_cat = CategorySerializer2(many=True)   #一类下面可能有很多二类，所以此处要定义many=True,否则报错
                                    #此处用到 "sub_cat ",model定义中的 related_name
                                    #嵌套自己
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsImageSerializer(serializers.ModelSerializer):  #GoodsImage的Serializer
    class Meta:
        model = GoodsImage
        fields = ("image",)    #只需要一个image就可以了



class GoodsSerializer(serializers.ModelSerializer):   #serializers中的ModelSerializer比serializers中的Serializer，用起来更简单，控制性更高
    #使用与modelform一致
    category = CategorySerializer()   #实例化  ，将自定义的category覆盖fields中的category，嵌套CategorySerializer，可以展示外键的详情，
                                            #而不只是展示外键的ID，比django的serializer强大
                                    #序列化的嵌套
    images = GoodsImageSerializer(many=True)   #序列化传递many=True表示可以取多条
                                                #外键的嵌套，用到 model中的related_name的值
    class Meta:
        model = Goods   #指明model
        # fields = ('name','click_num','market_price','add_time')   #指明字段
        fields = "__all__"   #取出model中的所有字段，不管是什么字段都不会序列化出错，而且会将外键序列化成他的ID
                                #图片类型的路径加上media配置的路径
                                #时间类型也不会出错


#轮播图
class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


#GoodsCategoryBrand序列化
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


#首页商品
class IndexCategorySerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True)   #一个category会有多个brands，所以此处要设置many=True
                                            #懂得什么时候many=True，什么时候many=False
    # goods = GoodsSerializer()   #goods不能直接使用GoodsSerializer()，那是因为在选择类目的时候，往往选的是最小的类目，
                                #所以外键指的时候包含了一二三类，不只是只有一类
                                #此处拿到的是第一级的分类，可能取不到数据
                                #所以需要自己查询，使用serializers.SerializerMethodField()
    goods = serializers.SerializerMethodField()   #取一类（一级）商品
    sub_cat = CategorySerializer2(many=True)   #取二级商品
                                                #在Serializer中调用Serializer，就不会在返回的路径中加上域名
    ad_goods = serializers.SerializerMethodField()   #自定义ad_goods序列化数据

    def get_ad_goods(self,obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)   #取到category_id等于实例化id的数据
        if ad_goods:
            goods_ins = ad_goods[0].goods
            goods_json = GoodsSerializer(goods_ins,many=False,context={'request': self.context['request']}).data   #取到序列化数据data,此处的many=False，一对一
                         # 在Serializer中调用Serializer，就不会在返回的路径中加上域名，要想加上域名，要在上下文中传入reuqest ,context={'request': self.context['request']}
                         #在源码中，如果判断出有reuqest，则会自动加上域名，但是自定义的需要使用context={'request': self.context['request']}加上域名，不然不会有域名
                         #Serializer中嵌套Serializer不会加域名，view中调用Serializer，会加
        return goods_json   #返回json 数据

    def get_goods(self,obj):   #自定义goods的序列方法
        all_goods = Goods.objects.filter(Q(category_id = obj.id)| Q(category__parent_category_id = obj.id)| Q(category__parent_category__parent_category_id = obj.id))
                # category_id等于传进来的value 或者 category的父的category_id等于传进来的value或者category的父的category的父的category_id等于传进来的value
        goods_serializer = GoodsSerializer(all_goods,many=True,context={'request': self.context['request']})   #自定义序列化， 将只有一类的数据序列化
                        # 在Serializer中调用Serializer，就不会在返回的路径中加上域名，要想加上域名，要在上下文中传入reuqest ,context={'request': self.context['request']}
                        # 在源码中，如果判断出有reuqest，则会自动加上域名，但是自定义的需要使用context={'request': self.context['request']}加上域名，不然不会有域名
                        # Serializer中嵌套Serializer不会加域名，view中调用Serializer，会加
        return goods_serializer.data   #返回序列化，返回只有一类数据的序列化

    class Meta:
        model = GoodsCategory
        fields = "__all__"










