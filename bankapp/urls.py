from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ============ PUBLIC PAGES ============
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),  # <-- MUST BE BEFORE my-account/
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # ============ AUTHENTICATION ============
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='bankapp/password_reset.html',
             email_template_name='bankapp/password_reset_email.html',
             subject_template_name='bankapp/password_reset_subject.txt'
         ), name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='bankapp/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='bankapp/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='bankapp/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # ============ USER DASHBOARD - CUSTOMERS ONLY ============
    path('my-banking/', views.dashboard, name='dashboard'),
    path('my-profile/', views.profile, name='profile'),
    path('my-profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-account/deposit/', views.deposit, name='deposit'),
    path('my-account/withdraw/', views.withdraw, name='withdraw'),
    path('my-account/transfer/', views.transfer, name='transfer'),  # <-- SPECIFIC PATH
    path('my-account/transactions/', views.transaction_history, name='transaction_history'),
    path('my-account/transaction/<str:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('my-account/download-report/', views.download_report, name='download_report'),
    
    # ============ BANK ADMINISTRATOR - STAFF ONLY ============
    path('bank-staff/', views.admin_dashboard, name='admin_dashboard'),
    path('bank-staff/users/', views.manage_users, name='manage_users'),
    # ... rest of admin URLs
]