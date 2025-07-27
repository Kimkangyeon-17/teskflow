from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "사용자 관리"

    def ready(self):
        # 시그널 연결 (필요시)
        try:
            import apps.users.signals
        except ImportError:
            pass
