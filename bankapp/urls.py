from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # ==================================================
    # PUBLIC PAGES
    # ==================================================
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),

    # ==================================================
    # AUTHENTICATION
    # ==================================================
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path(
        'password-change/',
        views.CustomPasswordChangeView.as_view(),
        name='password_change'
    ),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='bankapp/password_reset.html',
            email_template_name='bankapp/password_reset_email.html',
            subject_template_name='bankapp/password_reset_subject.txt'
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='bankapp/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='bankapp/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='bankapp/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # ==================================================
    # CUSTOMER DASHBOARD (CUSTOMERS ONLY)
    # ==================================================
    path('my-banking/', views.dashboard, name='dashboard'),
    path('my-profile/', views.profile, name='profile'),
    path('my-profile/edit/', views.edit_profile, name='edit_profile'),

    path('my-account/deposit/', views.deposit, name='deposit'),
    path('my-account/withdraw/', views.withdraw, name='withdraw'),
    path('my-account/transfer/', views.transfer, name='transfer'),

    path('my-account/transactions/', views.transaction_history, name='transaction_history'),
    path(
        'my-account/transaction/<str:transaction_id>/',
        views.transaction_detail,
        name='transaction_detail'
    ),
    path('my-account/download-report/', views.download_report, name='download_report'),

    # ==================================================
    # BANK ADMIN / STAFF (STAFF ONLY)
    # ==================================================
    path('bank-staff/', views.admin_dashboard, name='admin_dashboard'),

    # USERS
    path('bank-staff/users/', views.manage_users, name='manage_users'),
    path(
        'bank-staff/users/<int:user_id>/',
        views.manage_user_detail,
        name='manage_user_detail'
    ),
    path(
        'bank-staff/users/<int:user_id>/freeze/',
        views.toggle_freeze_account,
        name='toggle_freeze_account'
    ),
    path(
        'bank-staff/users/<int:user_id>/reset-password/',
        views.admin_reset_password,
        name='admin_reset_password'
    ),

    # ACCOUNT TYPES
    path(
        'bank-staff/account-types/',
        views.manage_account_types,
        name='manage_account_types'
    ),
    path(
        'bank-staff/account-types/add/',
        views.add_account_type,
        name='add_account_type'
    ),
    path(
        'bank-staff/account-types/<int:pk>/edit/',
        views.edit_account_type,
        name='edit_account_type'
    ),
    path(
        'bank-staff/account-types/<int:pk>/delete/',
        views.delete_account_type,
        name='delete_account_type'
    ),

    # TRANSACTIONS
    path(
        'bank-staff/transactions/',
        views.manage_transactions,
        name='manage_transactions'
    ),
    path(
        'bank-staff/transactions/<int:transaction_id>/rollback/',
        views.rollback_transaction,
        name='rollback_transaction'
    ),
    path(
        'bank-staff/transactions/<int:transaction_id>/edit/',
        views.edit_transaction,
        name='edit_transaction'
    ),
    path(
        'bank-staff/transactions/<int:transaction_id>/delete/',
        views.delete_transaction,
        name='delete_transaction'
    ),

    # AUDIT LOGS & REPORTS
    path('bank-staff/audit-logs/', views.audit_logs, name='audit_logs'),
    path('bank-staff/reports/', views.reports, name='reports'),
    path('bank-staff/export/csv/', views.export_csv, name='export_csv'),
    path('bank-staff/export/pdf/', views.export_pdf, name='export_pdf'),
]
