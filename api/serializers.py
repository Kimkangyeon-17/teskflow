from rest_framework import serializers

# 예시용 Serializer
# class ExampleSerializer(serializers.ModelSerializer):
#     """
#     예시용 Serializer - 실제 사용시 주석 해제하고 수정
#     """
#     class Meta:
#         # model = ExampleModel
#         # fields = '__all__'
#         pass


# 기본 응답 Serializer
class HealthCheckSerializer(serializers.Serializer):
    """
    헬스 체크 응답용 Serializer
    """

    status = serializers.CharField()
    message = serializers.CharField()
