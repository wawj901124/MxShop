import json
import requests

class YunPian(object):

    def __init__(self,api_key):   #初始化函数,传递一个api_key
        self.api_key = api_key
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self,code,mobile):   #设置发送短信接口
        parmas = {
            "apikey":self.api_key,
            "mobile":mobile,
            "text":"【慕学生鲜】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }

        response = requests.post(self.single_send_url,data=parmas)   #发起接口请求
        re_dict = json.loads(response.text)   #返回请求结果的内容
        # print(re_dict)
        return re_dict

if __name__ =="__main__":
    yun_pian = YunPian("d6c4ddbf50ab36611d2f52041a0b949e")
    yun_pian.send_sms("2019","18782902568")




