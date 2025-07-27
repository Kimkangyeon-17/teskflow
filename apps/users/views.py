from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import User, EmailVerificationToken
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserBasicSerializer,
    PasswordChangeSerializer,
    EmailVerificationSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    """
    사용자 회원가입 API
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 사용자 생성
        user = serializer.save()

        # 이메일 인증 토큰 생성 및 발송
        self.send_email_verification(user)

        return Response(
            {
                "success": True,
                "data": {
                    "user": UserBasicSerializer(user).data,
                    "message": "회원가입이 완료되었습니다. 이메일 인증을 완료해주세요.",
                },
            },
            status=status.HTTP_201_CREATED,
        )

    def send_email_verification(self, user):
        """이메일 인증 토큰 생성 및 발송"""
        # 기존 미사용 토큰 삭제
        EmailVerificationToken.objects.filter(
            user=user, email=user.email, is_used=False
        ).delete()

        # 새 토큰 생성
        token = EmailVerificationToken.objects.create(
            user=user, email=user.email, expires_at=timezone.now() + timedelta(hours=24)
        )

        # 이메일 발송 (개발 환경에서는 콘솔에 출력)
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email/{token.token}"

        subject = "TaskFlow 이메일 인증"
        message = f"""
        안녕하세요 {user.get_full_name()}님,
        
        TaskFlow에 가입해주셔서 감사합니다.
        아래 링크를 클릭하여 이메일 인증을 완료해주세요.
        
        {verification_url}
        
        이 링크는 24시간 동안 유효합니다.
        
        감사합니다.
        TaskFlow 팀
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"이메일 발송 실패: {e}")


class UserLoginView(TokenObtainPairView):
    """
    사용자 로그인 API (JWT 토큰 발급)
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)

        # 로그인 기록 업데이트
        user.last_login = timezone.now()

        # IP 주소 기록
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        user.last_login_ip = ip

        user.save(update_fields=["last_login", "last_login_ip"])

        return Response(
            {
                "success": True,
                "data": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserBasicSerializer(user).data,
                },
                "message": "로그인되었습니다.",
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    사용자 프로필 조회/수정 API
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "프로필이 업데이트되었습니다.",
            },
            status=status.HTTP_200_OK,
        )


class PasswordChangeView(APIView):
    """
    비밀번호 변경 API
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # 비밀번호 변경
        serializer.save()

        return Response(
            {"success": True, "message": "비밀번호가 변경되었습니다."},
            status=status.HTTP_200_OK,
        )


class EmailVerificationView(APIView):
    """
    이메일 인증 API
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 이메일 인증 처리
        user = serializer.save()

        return Response(
            {
                "success": True,
                "data": {"user": UserBasicSerializer(user).data},
                "message": "이메일 인증이 완료되었습니다.",
            },
            status=status.HTTP_200_OK,
        )


class ResendEmailVerificationView(APIView):
    """
    이메일 인증 재발송 API
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_email_verified:
            return Response(
                {"success": False, "message": "이미 인증된 이메일입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이메일 인증 재발송
        registration_view = UserRegistrationView()
        registration_view.send_email_verification(user)

        return Response(
            {"success": True, "message": "인증 이메일이 재발송되었습니다."},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def check_email_availability(request):
    """
    이메일 중복 확인 API
    """
    email = request.data.get("email")

    if not email:
        return Response(
            {"success": False, "message": "이메일을 입력해주세요."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    is_available = not User.objects.filter(email=email).exists()

    return Response(
        {
            "success": True,
            "data": {
                "email": email,
                "is_available": is_available,
                "message": (
                    "사용 가능한 이메일입니다."
                    if is_available
                    else "이미 사용 중인 이메일입니다."
                ),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
    """
    계정 삭제 API
    """
    user = request.user
    password = request.data.get("password")

    if not password:
        return Response(
            {"success": False, "message": "비밀번호를 입력해주세요."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.check_password(password):
        return Response(
            {"success": False, "message": "비밀번호가 올바르지 않습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 계정 삭제 (소프트 삭제 방식)
    user.is_active = False
    user.email = f"deleted_{user.id}_{user.email}"
    user.save()

    return Response(
        {"success": True, "message": "계정이 삭제되었습니다."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def auth_status(request):
    """
    인증 상태 확인 API
    """
    if request.user.is_authenticated:
        return Response(
            {
                "success": True,
                "data": {
                    "is_authenticated": True,
                    "user": UserBasicSerializer(request.user).data,
                },
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"success": True, "data": {"is_authenticated": False, "user": None}},
            status=status.HTTP_200_OK,
        )
