import pytz as tz
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            tzname = request.COOKIES.get("django_timezone")
            if tzname:
                timezone.activate(tz.timezone(tzname))
            else:
                timezone.deactivate()
        except Exception as e:
            timezone.deactivate()

        return self.get_response(request)
