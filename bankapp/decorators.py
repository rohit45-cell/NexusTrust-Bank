from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from functools import wraps

def customer_required(view_func):
    """Decorator to ensure ONLY regular customers can access - STAFF BLOCKED"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        
        # BLOCK STAFF AND SUPERUSERS FROM CUSTOMER PAGES
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, 'Staff members cannot access customer pages. Please use Bank Staff portal.')
            return redirect('admin_dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """Decorator to ensure ONLY staff/admin can access - REGULAR USERS BLOCKED"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login as staff to access this page.')
            return redirect('login')
        
        # BLOCK REGULAR CUSTOMERS FROM STAFF PAGES
        if not request.user.is_staff:
            messages.error(request, 'Access denied. Staff privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def superuser_required(view_func):
    """Decorator for Django admin - SUPERUSER ONLY"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Superuser privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def account_frozen_check(view_func):
    """Decorator to check if user account is frozen"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_frozen:
            messages.error(request, 'Your account is frozen. Please contact customer support.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def account_active_required(view_func):
    """Decorator to check if user account is active"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_active:
            messages.error(request, 'Your account is inactive. Please contact support.')
            return redirect('logout')
        return view_func(request, *args, **kwargs)
    return _wrapped_view