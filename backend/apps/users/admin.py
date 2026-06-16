from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'full_path', 'creator', 'member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']

    def full_path(self, obj):
        return obj.get_full_path()
    full_path.short_description = '完整路径'

    def member_count(self, obj):
        return obj.get_all_members().count()
    member_count.short_description = '成员数'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'department', 'role', 'get_role_display',
                    'is_banned', 'is_active', 'date_joined']
    list_editable = ['is_banned', 'role', 'department']
    list_filter = ['role', 'department', 'is_banned', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('角色与状态', {'fields': ('role', 'department', 'is_banned')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('角色', {'fields': ('role', 'department', 'is_banned')}),
    )

    def get_role_display(self, obj):
        return obj.get_role_display()
    get_role_display.short_description = '角色名称'
