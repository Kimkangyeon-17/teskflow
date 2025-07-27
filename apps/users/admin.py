from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    사용자 관리 어드민
    """

    # 목록 페이지 설정
    list_display = [
        "email",
        "get_full_name",
        "is_email_verified",
        "social_provider",
        "is_active",
        "is_staff",
        "created_at",
        "last_login",
    ]

    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "is_email_verified",
        "social_provider",
        "theme",
        "language",
        "created_at",
    ]

    search_fields = ["email", "first_name", "last_name"]

    ordering = ["-created_at"]

    # 상세 페이지 설정
    fieldsets = (
        ("기본 정보", {"fields": ("email", "first_name", "last_name", "avatar")}),
        ("프로필", {"fields": ("bio", "timezone", "theme", "language")}),
        (
            "권한",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "소셜 로그인",
            {"fields": ("social_provider", "social_id"), "classes": ("collapse",)},
        ),
        (
            "메타데이터",
            {
                "fields": (
                    "is_email_verified",
                    "created_at",
                    "updated_at",
                    "last_login",
                    "last_login_ip",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at", "last_login", "social_id"]

    # 사용자 추가 페이지 설정
    add_fieldsets = (
        (
            "기본 정보",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
        ("설정", {"fields": ("timezone", "theme", "language")}),
    )

    # 사용자명 필드 변경 (email 사용)
    username_field = "email"

    def get_full_name(self, obj):
        """전체 이름 표시"""
        return obj.get_full_name()

    get_full_name.short_description = "이름"


class UserProfileInline(admin.TabularInline):
    """
    사용자 프로필 인라인
    """

    model = UserProfile
    extra = 0
    fields = ["phone_number", "birth_date", "email_notifications", "push_notifications"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    사용자 프로필 관리 어드민
    """

    list_display = [
        "user",
        "phone_number",
        "email_notifications",
        "push_notifications",
        "created_at",
    ]

    list_filter = ["email_notifications", "push_notifications", "created_at"]

    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone_number",
    ]

    readonly_fields = ["created_at", "updated_at"]


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    이메일 인증 토큰 관리 어드민
    """

    list_display = [
        "user",
        "email",
        "token_display",
        "is_used",
        "is_expired_display",
        "created_at",
        "expires_at",
    ]

    list_filter = ["is_used", "created_at", "expires_at"]

    search_fields = ["user__email", "email", "token"]

    readonly_fields = ["token", "created_at", "is_expired_display"]

    ordering = ["-created_at"]

    def token_display(self, obj):
        """토큰 일부만 표시"""
        return f"{str(obj.token)[:8]}..."

    token_display.short_description = "토큰"

    def is_expired_display(self, obj):
        """만료 상태 표시"""
        if obj.is_expired():
            return format_html('<span style="color: red;">만료됨</span>')
        else:
            return format_html('<span style="color: green;">유효함</span>')

    is_expired_display.short_description = "상태"

    actions = ["mark_as_used"]

    def mark_as_used(self, request, queryset):
        """선택된 토큰들을 사용됨으로 표시"""
        updated = queryset.update(is_used=True)
        self.message_user(request, f"{updated}개의 토큰이 사용됨으로 처리되었습니다.")

    mark_as_used.short_description = "선택된 토큰들을 사용됨으로 표시"
