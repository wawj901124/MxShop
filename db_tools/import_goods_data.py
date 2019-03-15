#独立使用django的model
import sys
import os


pwd = os.path.dirname(os.path.relpath(__file__))
sys.path.append(pwd+"../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE","MxShop.settings")

import django
django.setup()

from goods.models import Goods,GoodsCategory,GoodsImage

from db_tools.data.product_data import row_data


for goods_detail in row_data:
    goods = Goods()   #实例化
    goods.name = goods_detail["name"]   #实例化的name等于 goods_detail中的name
    #实例化的market_price等于goods_detail中的market_price,但是要将“￥”转换为空串,将“元”转换为空串,然后将剩下的数字转换为int类型
    #接着再将int类型的数据转换为float类型的数据
    goods.market_price = float(int(goods_detail["market_price"].replace("￥","").replace("元","")))    #市场价格
    goods.shop_price = float(int(goods_detail["sale_price"].replace("￥","").replace("元","")))    #本店价格

    # 商品的简介对应goods_detail中的desc内容,如果goods_detail中的desc内容不为None，就设置为空串
    goods.goods_brief = goods_detail["desc"] if goods_detail["desc"] is not None else ""

    #商户的描述对应goods_detail中的goods_desc内容，如果goods_detail中的goods_desc内容不为空，就设置为空串
    goods.goods_desc = goods_detail["goods_desc"] if goods_detail["goods_desc"] is not None else ""

    #商品的封面图等于goods_detail中images中的第一张图，如果没有这么多图片，则设置为空串
    goods.goods_front_image = goods_detail["images"][0] if goods_detail["images"] else ""

    #商品类别的名字等于goods_detail中categorys中的倒数第一个
    category_name = goods_detail['categorys'][-1]

    #有了商品的名字
    #此处用filter()，不用get(),是因为filter()获取不到数据的时候，返回的是一个空的数组，不会抛异常，
    #如果用get()，情况一：数据库里没有；情况二:数据库里查到两条；这两种情况下都是会抛异常的，
    #用get()的话，外面必须加一个try catch,用filter()就不用加try catch
    category = GoodsCategory.objects.filter(name=category_name)
    if category:   #如果查到
        goods.category = category[0]   #商品的类别选搜索到的category的第一个
    goods.save()   #保存

    #图片有轮播图，现在将图片保存起来
    for goods_image in goods_detail["images"]:
        goods_image_instance = GoodsImage()   #实例化
        goods_image_instance.image = goods_image   #实例化对象中的image字段（图片路径）等于goods_image
        goods_image_instance.goods = goods   #实例化对象中的goods字段等于上述的goods
        goods_image_instance.save()   #保存实例化对象






