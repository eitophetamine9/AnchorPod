from django.contrib.auth import get_user_model

User = get_user_model()


class UserPrefetchMiddleware:
    """
    Eager-loads profile and settings on authenticated request.user in a single query.
    Eliminates redundant lazy-loading database queries in base.html and header nav.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, "user") and request.user.is_authenticated:
            # Only prefetch if not already cached on the user object
            if not hasattr(request.user, "_profile_cache") or not hasattr(request.user, "_settings_cache"):
                try:
                    prefetched_user = (
                        User.objects.select_related("profile", "settings")
                        .get(pk=request.user.pk)
                    )
                    request.user = prefetched_user
                except User.DoesNotExist:
                    pass
        return self.get_response(request)
