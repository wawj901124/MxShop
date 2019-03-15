# -*- coding: utf-8 -*-

# pip install pycryptodome
__author__ = 'bobby'

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url  #支付宝发的支付通知url，是个异步的请求
        self.app_private_key_path = app_private_key_path   #这是一个文件的路径，私钥文件名路径
        self.app_private_key = None
        self.return_url = return_url   #支付完成后，要跳到自己服务的一个页面：就要使用return_url，是个同步的接口的请求，只有在支付页面支付时才有效
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())   #获取私钥文件里的内容并进行加密生成私钥self.app_private_key

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read()) #获取阿里pay公钥文件里的内容并进行加密生成支付公钥self.alipay_public_key
                                                                #此key用于验证支付宝返回的路径


        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"   #如果是debug模式，就会使用沙箱的url，现在使用沙箱环境的url
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"   #如果不是，就用正式的url

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {   #biz_content ，支付宝接口中跟应用相关的请求参数，有四个必填字段 subject, out_trade_no, total_amount, return_url
            "subject": subject,
            "out_trade_no": out_trade_no,   #自己平台的一个订单号
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)   #biz_content，传递除必须字段外，更多的非必需的参数
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)  #获得最终的订单信息字符串

    def build_body(self, method, biz_content, return_url=None):   #build_body,生成支付宝支付接口对应的公共请求参数
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:   #如果有return_url，则将return_url放入到公共请求参数data中
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url   #支付完成后，要跳转到的页面url就是return_url

        return data   #用于生成整个请求的消息格式

    def sign_data(self, data):   #对生成的请求的消息格式进行签名，这个签名是支付宝的支付签名，比较重要
        data.pop("sign", None)   #sign签名的时候，参数里不能有sign字段，所有首先删除sign字段
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)   #排序后的请求参数
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)  #排完序后，要将字符串用&符号连接起来，即生成支付串
        sign = self.sign(unsigned_string.encode("utf-8"))   #对支付串进行签名
        # ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)  #使用quote_plus（）函数对生成的支付url进行一个预处理

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)   #再将sign的值加上，映照前面的删除sign字段，所以此处要加上sign
        return signed_string   #获得最终的订单信息字符串

    def ordered_data(self, data):   #对传入的参数进行排序，排序很关键，不排序会出错
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))  #key为传递的参数

        return sorted([(k, v) for k, v in data.items()])  #使用sorted函数对其进行排序

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key   #首先获取private_key
        signer = PKCS1_v1_5.new(key)   #使用private_key，new Key 之后 生成一个signer对象，即签名的对象
        signature = signer.sign(SHA256.new(unsigned_string))   #使用SHA256的算法生成一个签名
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "") #使用encodebytes（）对signature进行base64位编码，然后进行utf8编码，
                                                                        # 将byte类型转换为utf8的字符串，再使用replace("\n", "")将换行符去掉
        return sign   #sign即为签名的字符串，这个完成了，整个支付宝的签名就完成了

    def _verify(self, raw_content, signature):  #raw_content为排序后的字符串，signature为支付宝返回的url中的签名
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))  #将排序后的字符串raw_content，转换为utf8字符串
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):  #将支付宝返回的签名和自己生成的签名，进行对比，如果一样，就返回True,否则返回False
            return True
        return False

    def verify(self, data, signature):   #验证支付宝返回的url是否合法，验证return_url
        if "sign_type" in data:
            sign_type = data.pop("sign_type")   #将data中的sign_type字段删除
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)  #将参数进行排序
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)  #排序后生成一个需要签名的message
        return self._verify(message, signature)


if __name__ == "__main__":
    # return_url = 'http://127.0.0.1:8000/?total_amount=100.00&timestamp=2017-08-15+23%3A53%3A34&sign=e9E9UE0AxR84NK8TP1CicX6aZL8VQj68ylugWGHnM79zA7BKTIuxxkf%2FvhdDYz4XOLzNf9pTJxTDt8tTAAx%2FfUAJln4WAeZbacf1Gp4IzodcqU%2FsIc4z93xlfIZ7OLBoWW0kpKQ8AdOxrWBMXZck%2F1cffy4Ya2dWOYM6Pcdpd94CLNRPlH6kFsMCJCbhqvyJTflxdpVQ9kpH%2B%2Fhpqrqvm678vLwM%2B29LgqsLq0lojFWLe5ZGS1iFBdKiQI6wZiisBff%2BdAKT9Wcao3XeBUGigzUmVyEoVIcWJBH0Q8KTwz6IRC0S74FtfDWTafplUHlL%2Fnf6j%2FQd1y6Wcr2A5Kl6BQ%3D%3D&trade_no=2017081521001004340200204115&sign_type=RSA2&auth_app_id=2016080600180695&charset=utf-8&seller_id=2088102170208070&method=alipay.trade.page.pay.return&app_id=2016080600180695&out_trade_no=20170202185&version=1.0'
    # o = urlparse(return_url)   #使用urlparse（）函数将return_url中的所有参数取出来
    # print(o)
    # query = parse_qs(o.query)  #对o进行query，然后有 parse_qs（）函数就能获取到参数的值
    # print(query)
    # processed_query = {}
    # ali_sign = query.pop("sign")[0]   #把query中的sign字段的内容删除，并将sign的第一个值保存为ali_sign
    #                                     #使用pop()函数删除指定字段的键值对


    alipay = AliPay(
        appid="2016080600180695",
        app_notify_url="http://127.0.0.1:9000/alipay/return/",
        app_private_key_path="../trade/keys/private_2048.txt",   #应用私钥的路径
        alipay_public_key_path="../trade/keys/alipay_key_2048.txt",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=True,  # 默认False,
        return_url="http://127.0.0.1:9000/alipay/return/"
    )

    # for key, value in query.items():
    #     processed_query[key] = value[0]   #取出第0个转换为字符串，不然会是数组
    # print (alipay.verify(processed_query, ali_sign))

    #生成整个请求的字符串，只是字符串，要把生成的字符串放到re_url中
    url = alipay.direct_pay(    #阿里pay的直接支付接口
        subject="测试订单2",
        out_trade_no="201902191634sss",   #我们平台的订单号
        total_amount=0.01,
        return_url="http://127.0.0.1:9000/alipay/return/"   #支付完成后，要跳到自己服务的一个页面：就要使用return_url
    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)  #alipaydev为阿里pay的沙箱环境

    print(re_url)