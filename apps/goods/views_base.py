from django.views.generic.base import View     #导入django最底层的，最基本的View

from goods.models import Goods   #导出Goods的 models

class GoodsListView(View):   #商品列表视图，继承View
    def get(self,request):    #重写get方法
        """
        通过django的view实现商品列表页
        :return:
        """
        json_list = []
        # goods = Goods.objects.all()   #获取所有商品
        goods = Goods.objects.all()[:10]   #获取10条
        # for good in goods:   #遍历获取商品
        #     json_dict = {}   #定义字典
        #     json_dict["name"] = good.name   #商品的名字
        #     json_dict["category"] = good.category.name   #商品的类别名字
        #     json_dict["market_price"] = good.market_price   #商品的市场价格
        #     # json_dict["add_time"] = good.add_time  #把时间加入字典后，序列化会报错
        #     json_list.append(json_dict)   #把json_dict添加到json_list中

        from django.forms.models import model_to_dict    #可以将model转换为一个dict,可以很轻松的提取model中的字段
        for good in goods:
            json_dict = model_to_dict(good)
            json_list.append(json_dict)
        import json
        from django.core.serializers import serialize   #导入django的序列化serialize,可以将全部类型的数据序列化
        json_data = serialize("json",goods)   #直接将模块序列化，将goods模块中的数据直接转换为json串

        # #HttpResponse调用
        # # json_data = json.loads(json_data)    #使用json的loads的方法加载序列化数据json_data
        #         #(1)json.dumps()函数是将一个Python数据类型列表进行json格式的编码（可以这么理解，json.dumps()函数是将字典转化为字符串）
        #         #(2)json.loads()函数是将json格式数据转换为字典（可以这么理解，json.loads()函数是将字符串转化为字典）
        # from django.http import HttpResponse ,JsonResponse  #导入django的HttpResponse,JsonResponse(只需要传入字典即可)
        # # import json   #导入json
        # # return HttpResponse(json.dumps(json_list),content_type="application/json")   #如果返回json串，则必须要指明content_type为application/json（json的格式串）
        # # return HttpResponse(json.dumps(json_data),content_type="application/json")  # 如果返回json串，则必须要指明content_type为application/json（json的格式串）
        # return HttpResponse(json_data, content_type="application/json")

        #JsonResponse调用，这个方法更好
        json_data = json.loads(json_data)    #使用json的loads的方法加载序列化数据json_data
                #(1)json.dumps()函数是将一个Python数据类型列表进行json格式的编码（可以这么理解，json.dumps()函数是将字典转化为字符串）
                #(2)json.loads()函数是将json格式数据转换为字典（可以这么理解，json.loads()函数是将字符串转化为字典）
        from django.http import HttpResponse ,JsonResponse  #导入django的HttpResponse,JsonResponse(只需要传入字典即可)
        # import json   #导入json
        # return HttpResponse(json.dumps(json_list),content_type="application/json")   #如果返回json串，则必须要指明content_type为application/json（json的格式串）
        # return HttpResponse(json.dumps(json_data),content_type="application/json")  # 如果返回json串，则必须要指明content_type为application/json（json的格式串）
        return JsonResponse(json_data,safe=False)   #此处设置safe为False，不然会报错“In order to allow non-dict objects to be serialized set the safe parameter to False.”