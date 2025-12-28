from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, EmotionRecord

# 定义内联用户配置文件
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '个人资料'

# 定义自定义UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

# 注册自定义UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 注册EmotionRecord模型
@admin.register(EmotionRecord)
class EmotionRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'emotion', 'confidence', 'created_at', 'is_deleted')
    list_filter = ('emotion', 'is_deleted', 'created_at')
    search_fields = ('user__username', 'emotion', 'image_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'deleted_at')
    list_editable = ('is_deleted',)
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'emotion', 'confidence', 'image_name')
        }),
        ('图片信息', {
            'fields': ('image_data', 'image_content_type')
        }),
        ('时间信息', {
            'fields': ('created_at', 'is_deleted', 'deleted_at')
        }),
    )
