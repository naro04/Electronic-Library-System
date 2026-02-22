from .models import PageVisit

class SimpleVisitLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            path = request.path
            if path.startswith('/static/') or path.startswith('/media/'):
                return response

            ip = request.META.get("REMOTE_ADDR", "")
            ua = (request.META.get("HTTP_USER_AGENT", "") or "")[:2000]
            user = request.user if request.user.is_authenticated else None

            PageVisit.objects.create(
                path=path,
                ip=ip,
                user_agent=ua,
                user=user
            )
        except Exception:
            pass

        return response