from rest_framework.permissions import IsAuthenticated


class IsOwnerOrAuthenticated(IsAuthenticated):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        is_authenticated = super().has_object_permission(request, view, obj)
        return is_authenticated or (is_authenticated and obj.created_by == request.user)


class NotOwnerAndAuthenticated(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        """
        Нельзя приобрести свой QR-код. Он доступен пользователю по умолчанию
        """
        is_authenticated = super().has_object_permission(request, view, obj)
        return obj.created_by != request.user and is_authenticated
