from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.http import JsonResponse


# 헬스 체크용 뷰 (서버가 잘 돌아가는지 확인)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    API 서버 상태 확인용 엔드포인트
    """
    return Response(
        {"status": "ok", "message": "Django API server is running!"},
        status=status.HTTP_200_OK,
    )


# 예시용 ViewSet (나중에 실제 모델로 교체)
# class ExampleViewSet(viewsets.ModelViewSet):
#     """
#     예시용 ViewSet - 실제 사용시 주석 해제하고 수정
#     """
#     # queryset = ExampleModel.objects.all()
#     # serializer_class = ExampleSerializer
#     pass
