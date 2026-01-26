import os
from django.core.exceptions import PermissionDenied
from django.conf import settings

class OfficeOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        
        if x_forwarded_for:
            visitor_ip = x_forwarded_for.split(',')[0].strip()
        else:
            visitor_ip = request.META.get('REMOTE_ADDR')

        # We will now look for a comma-separated list of allowed prefixes
        # Example: "105.117., 105.112., 102.89."
        allowed_prefixes_str = os.environ.get('ALLOWED_IP_PREFIXES', '')
        allowed_prefixes = [p.strip() for p in allowed_prefixes_str.split(',') if p.strip()]

        if not settings.DEBUG and allowed_prefixes:
            # Check if the visitor's IP starts with ANY of our allowed prefixes
            is_allowed = any(visitor_ip.startswith(prefix) for prefix in allowed_prefixes)
            
            if not is_allowed:
                # Optional: Print to logs so you can see blocked IPs for debugging
                print(f"Blocking unauthorized access from IP: {visitor_ip}")
                raise PermissionDenied
        
        return self.get_response(request)