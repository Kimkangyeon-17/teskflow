from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import FileExtensionValidator
import uuid


class UserManager(BaseUserManager):
    """
    Custom User Manager - 이메일 기반 사용자 관리
    """

    def create_user(self, email, password=None, **extra_fields):
        """일반 사용자 생성"""
        if not email:
            raise ValueError("이메일 주소는 필수입니다.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """슈퍼유저 생성"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # first_name, last_name이 없으면 기본값 설정
        extra_fields.setdefault("first_name", "Admin")
        extra_fields.setdefault("last_name", "User")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("슈퍼유저는 is_staff=True여야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("슈퍼유저는 is_superuser=True여야 합니다.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    확장된 사용자 모델
    이메일 기반 로그인 지원
    """

    # 기본 username 필드는 사용하지 않음
    username = None

    # 이메일을 유니크한 사용자명으로 사용
    email = models.EmailField(
        "이메일", unique=True, help_text="로그인에 사용될 이메일 주소"
    )

    # 이름 필드들
    first_name = models.CharField("이름", max_length=30)
    last_name = models.CharField("성", max_length=30)

    # 프로필 정보
    avatar = models.ImageField(
        "프로필 이미지",
        upload_to="avatars/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif"])
        ],
        help_text="프로필 이미지 (jpg, png, gif 지원)",
    )

    bio = models.TextField(
        "자기소개", max_length=500, blank=True, help_text="간단한 자기소개"
    )

    # 설정
    timezone = models.CharField(
        "시간대", max_length=50, default="Asia/Seoul", help_text="사용자의 시간대"
    )

    theme = models.CharField(
        "테마",
        max_length=10,
        choices=[
            ("light", "라이트"),
            ("dark", "다크"),
            ("auto", "자동"),
        ],
        default="light",
    )

    language = models.CharField(
        "언어",
        max_length=10,
        choices=[
            ("ko", "한국어"),
            ("en", "English"),
        ],
        default="ko",
    )

    # 이메일 인증
    is_email_verified = models.BooleanField("이메일 인증 여부", default=False)

    # 소셜 로그인 정보
    social_provider = models.CharField(
        "소셜 로그인 제공자",
        max_length=20,
        choices=[
            ("google", "Google"),
            ("kakao", "Kakao"),
            ("naver", "Naver"),
            ("github", "GitHub"),
        ],
        null=True,
        blank=True,
    )

    social_id = models.CharField(
        "소셜 로그인 ID", max_length=100, null=True, blank=True
    )

    # 메타데이터
    created_at = models.DateTimeField("가입일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)
    last_login_ip = models.GenericIPAddressField(
        "마지막 로그인 IP", null=True, blank=True
    )

    # 이메일을 USERNAME_FIELD로 사용
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Custom Manager 사용
    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자들"

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """전체 이름 반환"""
        return f"{self.last_name}{self.first_name}".strip()

    def get_short_name(self):
        """짧은 이름 반환"""
        return self.first_name

    @property
    def avatar_url(self):
        """프로필 이미지 URL 반환"""
        if self.avatar:
            return self.avatar.url
        return None

    def is_social_user(self):
        """소셜 로그인 사용자인지 확인"""
        return bool(self.social_provider and self.social_id)


class UserProfile(models.Model):
    """
    사용자 프로필 확장 정보
    추후 필요한 정보들을 추가할 수 있는 확장 모델
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # 개인 설정
    phone_number = models.CharField(
        "전화번호", max_length=20, blank=True, help_text="연락처 (선택사항)"
    )

    birth_date = models.DateField("생년월일", null=True, blank=True)

    # 알림 설정
    email_notifications = models.BooleanField(
        "이메일 알림", default=True, help_text="이메일로 알림 받기"
    )

    push_notifications = models.BooleanField(
        "푸시 알림", default=True, help_text="브라우저 푸시 알림 받기"
    )

    # 개인화 설정 - 추후 workspaces 앱 생성 후 활성화 예정
    # default_workspace = models.ForeignKey(
    #     'workspaces.Workspace',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     help_text='기본 워크스페이스'
    # )

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        verbose_name = "사용자 프로필"
        verbose_name_plural = "사용자 프로필들"

    def __str__(self):
        return f"{self.user.get_full_name()}의 프로필"


class EmailVerificationToken(models.Model):
    """
    이메일 인증 토큰
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_tokens"
    )

    token = models.UUIDField("인증 토큰", default=uuid.uuid4, unique=True)

    email = models.EmailField("인증할 이메일")

    is_used = models.BooleanField("사용 여부", default=False)

    expires_at = models.DateTimeField("만료 시간")

    created_at = models.DateTimeField("생성 시간", auto_now_add=True)

    class Meta:
        db_table = "email_verification_tokens"
        verbose_name = "이메일 인증 토큰"
        verbose_name_plural = "이메일 인증 토큰들"

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    def is_expired(self):
        """토큰이 만료되었는지 확인"""
        from django.utils import timezone

        return timezone.now() > self.expires_at
