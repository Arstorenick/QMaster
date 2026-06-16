from rest_framework import serializers
from .models import SurveyTemplate, TemplateQuestion, TemplateOption


class TemplateOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateOption
        fields = ['id', 'title', 'order', 'score']


class TemplateQuestionSerializer(serializers.ModelSerializer):
    options = TemplateOptionSerializer(many=True, read_only=True)

    class Meta:
        model = TemplateQuestion
        fields = ['id', 'type', 'title', 'is_required', 'order',
                  'score', 'config', 'options']


class TemplateListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = SurveyTemplate
        fields = ['id', 'title', 'description', 'usage_count',
                  'question_count', 'created_at']

    def get_question_count(self, obj):
        return obj.questions.count()


class TemplateDetailSerializer(serializers.ModelSerializer):
    questions = TemplateQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyTemplate
        fields = ['id', 'title', 'description', 'questions',
                  'usage_count', 'created_at']
