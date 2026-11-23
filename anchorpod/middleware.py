from django.contrib.auth import get_user_model, _get_user_session_key, BACKEND_SESSION_KEY
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject

User = get_user_model()


def get_prefetched_user(request):
    """Fetches user with profile and settings in a single database query."""
    try:
        user_id = _get_user_session_key(request)
        if not user_id or BACKEND_SESSION_KEY not in request.session:
            return AnonymousUser()
        return (
            User.objects.select_related("profile", "settings")
            .get(pk=user_id)
        )
    except Exception:
        return AnonymousUser()


class UserPrefetchMiddleware:
    """
    Replaces lazy request.user with a single-query loader that eagerly fetches
    both 'profile' and 'settings'. Eliminates redundant sequential auth queries.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, "session"):
            request.user = SimpleLazyObject(lambda: get_prefetched_user(request))
        return self.get_response(request)
