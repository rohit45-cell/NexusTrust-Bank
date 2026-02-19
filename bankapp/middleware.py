from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import logout
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SessionTimeoutMiddleware:
    """
    Middleware to handle session timeout and security.
    Also helps prevent CSRF issues by cleaning up sessions properly.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip session check for certain paths
        skip_paths = ['/login/', '/logout/', '/signup/', '/admin/', '/static/', '/media/']
        
        if request.user.is_authenticated:
            # Check last activity
            last_activity = request.session.get('last_activity')
            now = timezone.now()
            
            if last_activity:
                try:
                    last_activity = datetime.fromisoformat(last_activity)
                    # Make sure last_activity is timezone-aware
                    if timezone.is_naive(last_activity):
                        last_activity = timezone.make_aware(last_activity)
                    
                    # Check if session expired
                    expiry_age = request.session.get_expiry_age()
                    if (now - last_activity).seconds > expiry_age:
                        # Session expired - logout user
                        logger.info(f"Session expired for user: {request.user.email}")
                        messages.warning(request, 'Your session has expired. Please login again.')
                        
                        # Clear session properly
                        request.session.flush()
                        logout(request)
                        
                        # Redirect to login
                        return redirect('login')
                except (ValueError, TypeError) as e:
                    # If last_activity is invalid, reset it
                    logger.warning(f"Invalid last_activity in session: {e}")
                    request.session['last_activity'] = now.isoformat()
            
            # Update last activity
            request.session['last_activity'] = now.isoformat()
            
            # Also store IP for security (optional)
            if 'user_ip' not in request.session:
                request.session['user_ip'] = self.get_client_ip(request)
        
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Security Headers
        response['X-XSS-Protection'] = '1; mode=block'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP Header (Content Security Policy) - Uncomment and customize as needed
        # response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
        
        return response


class CSRFTokenMiddleware:
    """Ensure CSRF token is set properly"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add CSRF token cookie if not present
        if not request.COOKIES.get('csrftoken') and hasattr(request, 'META'):
            from django.middleware.csrf import get_token
            get_token(request)  # This sets the CSRF cookie
        
        return response
