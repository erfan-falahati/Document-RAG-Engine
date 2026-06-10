from rest_framework import serializers
from .models import QuestionAnswer

class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(required=True)

class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ['id', 'question', 'answer', 'created_at']


