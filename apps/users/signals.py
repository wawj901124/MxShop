from django.db.models.signals import post_save   #导入post_save
from django.dispatch import receiver   #导入receiver
from rest_framework.authtoken.models import Token   #导入token
from django.contrib.auth import get_user_model   #导入get_user_model

User = get_user_model()

@receiver(post_save,sender = User)   #装饰器，sender表示传递过来的model,此处是User
def create_auth_token(sender,instance=None,created=False, **kwargs):   #created=False表示是不是新建
    if created:   #当是新建的时候
        password = instance.password   #instance就是我们的User
        instance.set_password(password)   #设置密码
        instance.save()    #保存
        # Token.objects.create(user=instance)   #创建token，此处不创建
