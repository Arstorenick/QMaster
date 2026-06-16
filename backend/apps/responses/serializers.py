from rest_framework import serializers
from .models import Submission, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'option', 'answer_text',
                  'answer_number', 'answer_file', 'answer_json']


class SubmissionCreateSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ['id', 'respondent_info', 'duration_seconds', 'answers']
        read_only_fields = ['id']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        request = self.context.get('request')
        validated_data['submit_ip'] = self.get_client_ip(request)
        submission = Submission.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(submission=submission, **answer_data)
        return submission

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class SubmissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'submit_time', 'submit_ip', 'duration_seconds']
