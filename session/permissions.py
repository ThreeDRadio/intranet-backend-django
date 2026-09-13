from rest_framework import permissions

from .models import Whitelist


class IsStaffOrTargetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "retrieve":
            return True
        else:
            return hasattr(request, "user") and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if hasattr(request, "user"):
            return request.user.is_staff or obj == request.user
        return False


class IsAuthenticatedOrWhitelist(permissions.IsAuthenticated):
    """Passes if the user is authenticated or in a whitelist of IPs"""

    def has_permission(self, request, view):
        if is_whitelisted(get_ip_from_request(request)):
            return True
        
        return super(IsAuthenticatedOrWhitelist, self).has_permission(request, view)


def get_ip_from_request(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        requester = x_forwarded_for.split(",")[0].strip()
    else:
        requester = request.META.get("REMOTE_ADDR")

    return requester


def is_whitelisted(ip_address):
    return (
        ip_address is not None
        and Whitelist.objects.filter(ip=ip_address).exists()
    )
