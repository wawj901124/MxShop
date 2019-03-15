from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = '用户管理'

    def ready(self):
        import users.signals   #导入signals,signals是用来接收信号的，在这里可以写一些逻辑
                                #好处就是代码的分离性比较好
