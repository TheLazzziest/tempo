from rest_framework import permissions


class IsWalletOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `user_id`.
        return obj.user == request.user


class IsWalletActive(permissions.BasePermission):
    """
    Object-level permission to only allow access to active wallets.
    Assumes the model instance has a `status` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return obj.status == "A"
