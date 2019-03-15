#独立使用django的model
import sys
import os


pwd = os.path.dirname(os.path.relpath(__file__))
sys.path.append(pwd+"../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE","MxShop.settings")

import django
django.setup()

from goods.models import GoodsCategory

from db_tools.data.category_data import row_data

#对数据遍历入库
for lev1_cat in row_data:   #第一个类别
    lev1_instance = GoodsCategory()   #数据库的对象等于GoodsCategory
    lev1_instance.code = lev1_cat["code"]   #实例的code等于lev1_cat中的code
    lev1_instance.name = lev1_cat["name"]  # 实例的name等于lev1_cat中的name
    lev1_instance.category_type = 1   #实例的类型选择一级目录 “1”
    lev1_instance.save()    #保存到数据库

    #遍历子类
    for lev2_cat in lev1_cat["sub_categorys"]:   #遍历子类
        lev2_instance = GoodsCategory()  # 数据库的对象等于GoodsCategory
        lev2_instance.code = lev2_cat["code"]  # 实例的code等于lev2_cat中的code
        lev2_instance.name = lev2_cat["name"]  # 实例的name等于lev2_cat中的name
        lev2_instance.category_type = 2  # 实例的类型选择二级目录 “2”
        lev2_instance.parent_category = lev1_instance   # lev2的父类是lev1
        lev2_instance.save()  # 保存到数据库

        #遍历lev2的子类
        for lev3_cat in lev2_cat["sub_categorys"]:  # 遍历子类
            lev3_instance = GoodsCategory()  # 数据库的对象等于GoodsCategory
            lev3_instance.code = lev3_cat["code"]  # 实例的code等于lev3_cat中的code
            lev3_instance.name = lev3_cat["name"]  # 实例的name等于lev3_cat中的name
            lev3_instance.category_type = 3  # 实例的类型选择三级目录 “3”
            lev3_instance.parent_category = lev2_instance  # lev3的父类是lev2
            lev3_instance.save()  # 保存到数据库



