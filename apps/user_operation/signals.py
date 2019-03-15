from django.db.models.signals import post_save ,post_delete  #导入post_save,post_delete
from django.dispatch import receiver   #导入receiver
from rest_framework.authtoken.models import Token   #导入token
from django.contrib.auth import get_user_model   #导入get_user_model

# User = get_user_model()

from user_operation.models import UserFav

#用户收藏后，收藏数加1
@receiver(post_save,sender = UserFav)   #装饰器，sender表示传递过来的model,此处是UserFav，获取post_save的信号量
def create_userfav(sender,instance=None,created=False, **kwargs):   #created=False表示是不是新建
    if created:   #当是新建的时候,即首次添加的时候
        goods = instance.goods   #当用户创建收藏的时候，找到相应的商品（goods）,然后将其收藏数加1
                                #goods是UserFav Model中的goods字段
        goods.fav_num +=1   #收藏数加1
        goods.save()   #保存

#用户删除后，收藏减一
@receiver(post_delete,sender = UserFav)   #装饰器，sender表示传递过来的model,此处是UserFav，获取post_delete的信号量
def delete_userfav(sender,instance=None,created=False, **kwargs):   #created=False表示是不是新建
    goods = instance.goods   #当用户创建收藏的时候，找到相应的商品（goods）,然后将其收藏数加1
                            #goods是UserFav Model中的goods字段
    goods.fav_num -=1   #收藏数减1
    goods.save()   #保存