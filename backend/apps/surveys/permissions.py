from rest_framework import permissions


class IsSurveyOwner(permissions.BasePermission):
    """只有问卷所有者可以编辑"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsSurveyOwnerOrPublicRead(permissions.BasePermission):
    """问卷所有者可编辑，已发布问卷公开可读"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.status == 1 or obj.owner == request.user
        return obj.owner == request.user
