from rest_framework import permissions



class IsEditor (permissions.BasePermission):
    """ allow view to editors only """

    def has_permission(self, request, view):
        user_role = request.user.role 
        if user_role == "e":
            return True
        return False

class IsPro (permissions.BasePermission):
    """ allow view to pro and premium users"""

    def has_permission(self, request, view):
        user_plan = request.user.plan.plan_version
        if (user_plan=="1") or (user_plan=="2"):
            return True
        return False

class IsPremium (permissions.BasePermission):
    """allow view just to premium users"""

    def has_permission(self, request, view):
        user_plan = request.user.plan.plan_version
        if user_plan == "2":
            return True
        return False

class IsSuperUser (permissions.BasePermission):

    def has_permission(self, request, view):
        is_superuser = request.user.is_superuser
        return is_superuser   