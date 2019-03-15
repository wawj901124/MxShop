from django.apps import AppConfig


class UserOperationConfig(AppConfig):
    name = 'user_operation'
    verbose_name = '用户操作管理'

    def ready(self):
        import user_operation.signals   #导入signals,signals是用来接收信号的，在这里可以写一些逻辑
                                #好处就是代码的分离性比较好

