from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AccountType, Transaction, Contact, AuditLog, InterestHistory


# =========================
# USER ADMIN
# =========================
class UserAdmin(BaseUserAdmin):
    list_display = [
        'account_number', 'full_name', 'email', 'phone',
        'account_type', 'balance', 'is_active', 'is_frozen', 'date_joined'
    ]
    list_filter = ['is_active', 'is_frozen', 'account_type', 'date_joined']
    search_fields = ['account_number', 'full_name', 'email', 'phone', 'aadhaar', 'pan']
    ordering = ['-date_joined']

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'full_name', 'email', 'phone',
                'aadhaar', 'pan',
                'address', 'city', 'state', 'pincode',
                'profile_picture'
            )
        }),
        ('Banking Details', {
            'fields': (
                'account_number', 'ifsc_code',
                'account_type', 'balance'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_frozen',
                'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'full_name',
                'password1', 'password2',
                'is_staff', 'is_superuser'
            ),
        }),
    )

    readonly_fields = [
        'account_number',
        'ifsc_code',
        'date_joined',
        'last_login'
    ]

    # ✅ FIXED METHOD (NO ERROR)
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing user
            return self.readonly_fields + ['email']
        return self.readonly_fields


# =========================
# ACCOUNT TYPE ADMIN
# =========================
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category',
        'minimum_balance', 'interest_rate',
        'overdraft_limit', 'is_active'
    ]
    list_filter = ['category', 'is_active']
    search_fields = ['name']


# =========================
# TRANSACTION ADMIN
# =========================
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'user',
        'transaction_type', 'amount',
        'balance_after', 'status', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = [
        'transaction_id',
        'user__full_name',
        'user__account_number'
    ]
    readonly_fields = [
        'transaction_id',
        'created_at',
        'updated_at'
    ]

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


# =========================
# CONTACT ADMIN
# =========================
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'phone',
        'subject', 'is_resolved', 'created_at'
    ]
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['name', 'email', 'subject']
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)

    mark_as_resolved.short_description = "Mark selected as resolved"


# =========================
# AUDIT LOG ADMIN
# =========================
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'admin_user',
        'action_type', 'target_model',
        'target_object_repr'
    ]
    list_filter = ['action_type', 'target_model', 'timestamp']
    search_fields = [
        'admin_user__email',
        'target_object_repr',
        'description'
    ]
    readonly_fields = ['timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# =========================
# INTEREST HISTORY ADMIN
# =========================
class InterestHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'amount', 'rate',
        'period_start', 'period_end', 'credited_at'
    ]
    list_filter = ['credited_at']
    search_fields = [
        'user__full_name',
        'user__account_number'
    ]
    readonly_fields = ['credited_at']


# =========================
# REGISTER MODELS
# =========================
admin.site.register(User, UserAdmin)
admin.site.register(AccountType, AccountTypeAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(InterestHistory, InterestHistoryAdmin)


# =========================
# ADMIN SITE BRANDING
# =========================
admin.site.site_header = 'NexusTrust Bank Administration'
admin.site.site_title = 'NexusTrust Bank Admin'
admin.site.index_title = 'Banking System Administration'
