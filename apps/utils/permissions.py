from rest_framework import permissions   #导入permissions


#自定义的权限
class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):   #obj为model
        if request.method in permissions.SAFE_METHODS:   #如果是安全的请求方法（'GET', 'HEAD', 'OPTIONS'）
            return True
        return obj.user == request.user   #否则会判断model的user是否等于请求的user
