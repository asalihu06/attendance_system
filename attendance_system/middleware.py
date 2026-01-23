import os
from django.core.exceptions import PermissionDenied
from django.conf import settings

class OfficeOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Render uses a proxy, so we must check HTTP_X_FORWARDED_FOR
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        
        if x_forwarded_for:
            # The first IP in the list is the actual user
            visitor_ip = x_forwarded_for.split(',')[0].strip()
        else:
            visitor_ip = request.META.get('REMOTE_ADDR')

        allowed_ip = os.environ.get('OFFICE_IP')

        # Logic: If we are in production (DEBUG=False) and the IP doesn't match, block them.
        if not settings.DEBUG and allowed_ip:
            if visitor_ip != allowed_ip:
                raise PermissionDenied
        
        return self.get_response(request)