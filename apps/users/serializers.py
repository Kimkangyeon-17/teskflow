from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    사용자 회원가입 시리얼라이저
    """

    password = serializers.CharField(
        write_only=True, min_length=8, help_text="최소 8자 이상, 영문+숫자 조합"
    )
    password_confirm = serializers.CharField(write_only=True, help_text="비밀번호 확인")

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "timezone",
            "theme",
            "language",
        ]

    def validate_email(self, value):
        """이메일 중복 검사"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_password(self, value):
        """비밀번호 유효성 검사"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, attrs):
        """비밀번호 확인 검사"""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "비밀번호가 일치하지 않습니다."}
            )
        return attrs

    def create(self, validated_data):
        """사용자 생성"""
        # password_confirm 제거
        validated_data.pop("password_confirm")

        # 사용자 생성
        user = User.objects.create_user(**validated_data)

        # 프로필 생성
        UserProfile.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    사용자 로그인 시리얼라이저
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """로그인 인증"""
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                username=email,  # USERNAME_FIELD가 email이므로
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    "이메일 또는 비밀번호가 올바르지 않습니다."
                )

            if not user.is_active:
                raise serializers.ValidationError("비활성화된 계정입니다.")

            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")


class UserProfileSerializer(serializers.ModelSerializer):
    """
    사용자 프로필 시리얼라이저 (조회/수정용)
    """

    avatar_url = serializers.ReadOnlyField()
    full_name = serializers.SerializerMethodField()
    is_social_user = serializers.SerializerMethodField()

    # 프로필 확장 정보
    phone_number = serializers.CharField(
        source="profile.phone_number", allow_blank=True, required=False
    )
    birth_date = serializers.DateField(
        source="profile.birth_date", allow_null=True, required=False
    )
    email_notifications = serializers.BooleanField(
        source="profile.email_notifications", required=False
    )
    push_notifications = serializers.BooleanField(
        source="profile.push_notifications", required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "avatar_url",
            "bio",
            "timezone",
            "theme",
            "language",
            "is_email_verified",
            "is_social_user",
            "social_provider",
            "phone_number",
            "birth_date",
            "email_notifications",
            "push_notifications",
            "created_at",
            "updated_at",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "email",
            "is_email_verified",
            "social_provider",
            "created_at",
            "updated_at",
            "last_login",
        ]

    def get_full_name(self, obj):
        """전체 이름 반환"""
        return obj.get_full_name()

    def get_is_social_user(self, obj):
        """소셜 로그인 사용자 여부"""
        return obj.is_social_user()

    def update(self, instance, validated_data):
        """프로필 업데이트"""
        # 프로필 관련 데이터 분리
        profile_data = validated_data.pop("profile", {})

        # 사용자 기본 정보 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 프로필 정보 업데이트
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class UserBasicSerializer(serializers.ModelSerializer):
    """
    기본 사용자 정보 시리얼라이저 (다른 API에서 사용자 정보 포함시 사용)
    """

    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "avatar_url"]

    def get_full_name(self, obj):
        return obj.get_full_name()


class PasswordChangeSerializer(serializers.Serializer):
    """
    비밀번호 변경 시리얼라이저
    """

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, min_length=8, help_text="최소 8자 이상, 영문+숫자 조합"
    )
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        """현재 비밀번호 확인"""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 올바르지 않습니다.")
        return value

    def validate_new_password(self, value):
        """새 비밀번호 유효성 검사"""
        try:
            validate_password(value, user=self.context["request"].user)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, attrs):
        """새 비밀번호 확인"""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "새 비밀번호가 일치하지 않습니다."}
            )
        return attrs

    def save(self):
        """비밀번호 변경"""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """
    이메일 인증 시리얼라이저
    """

    token = serializers.UUIDField()

    def validate_token(self, value):
        """토큰 유효성 검사"""
        from .models import EmailVerificationToken
        from django.utils import timezone

        try:
            token = EmailVerificationToken.objects.get(
                token=value, is_used=False, expires_at__gt=timezone.now()
            )
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("유효하지 않거나 만료된 토큰입니다.")

        self.context["token_obj"] = token
        return value

    def save(self):
        """이메일 인증 처리"""
        token = self.context["token_obj"]
        user = token.user

        # 사용자 이메일 인증 처리
        user.is_email_verified = True
        user.save()

        # 토큰 사용 처리
        token.is_used = True
        token.save()

        return user
