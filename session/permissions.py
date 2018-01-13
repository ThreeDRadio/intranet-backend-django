from rest_framework  import permissions
from .models import Whitelist

class IsStaffOrTargetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'retrieve':
            return True
        else:
            return hasattr(request, 'user') and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if hasattr(request, 'user'):
            return request.user.is_staff or obj == request.user
        return False


class IsAuthenticatedOrWhitelist(permissions.IsAuthenticated):
    """ Passes if the user is authenticated or in a whitelist of IPs """
    def has_permission(self, request, view):
        ipAddress = request.META['REMOTE_ADDR']
        whitelisted = Whitelist.objects.filter(ip=ipAddress).exists()
        if whitelisted:
            return True
        return super(IsAuthenticatedOrWhitelist, self).has_permission(request, view)
    
