from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

class SessionTimeoutMiddleware:
    """Middleware to handle session timeout"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Check last activity
            last_activity = request.session.get('last_activity')
            now = timezone.now()
            
            if last_activity:
                last_activity = datetime.fromisoformat(last_activity)
                if (now - last_activity).seconds > request.session.get_expiry_age():
                    # Session expired
                    messages.warning(request, 'Your session has expired. Please login again.')
                    return redirect('logout')
            
            request.session['last_activity'] = now.isoformat()
        
        response = self.get_response(request)
        return response