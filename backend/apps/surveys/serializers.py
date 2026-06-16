from rest_framework import serializers
from .models import Survey, Question, Option


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'title', 'order', 'score', 'image']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'type', 'title', 'is_required', 'order',
                  'score', 'config', 'options', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)
        for i, opt in enumerate(options_data):
            opt.setdefault('order', i)
            Option.objects.create(question=question, **opt)
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if options_data is not None:
            instance.options.all().delete()
            for i, opt in enumerate(options_data):
                opt.setdefault('order', i)
                Option.objects.create(question=instance, **opt)
        return instance


class SurveyListSerializer(serializers.ModelSerializer):
    """问卷列表（不含题目详情）"""
    question_count = serializers.SerializerMethodField()
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'status', 'style',
                  'question_count', 'submission_count', 'published_at',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'question_count', 'submission_count',
                            'created_at', 'updated_at']

    def get_question_count(self, obj):
        return obj.questions.count()

    def get_submission_count(self, obj):
        return obj.submissions.count()


class SurveyDetailSerializer(serializers.ModelSerializer):
    """问卷详情（含所有题目和选项）"""
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    submission_count = serializers.SerializerMethodField()
    target_departments = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'status', 'style',
                  'questions', 'question_count', 'submission_count',
                  'target_departments', 'owner_name', 'published_at',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'question_count', 'submission_count',
                            'created_at', 'updated_at']

    def get_question_count(self, obj):
        return obj.questions.count()

    def get_submission_count(self, obj):
        return obj.submissions.count()

    def get_target_departments(self, obj):
        return list(obj.target_departments.values_list('id', flat=True))

    def get_owner_name(self, obj):
        return obj.owner.username


class StyleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['style']


class ReorderSerializer(serializers.Serializer):
    """拖拽排序"""
    question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='按新顺序排列的题目 ID 列表'
    )
