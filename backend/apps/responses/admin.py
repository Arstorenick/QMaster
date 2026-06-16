from django.contrib import admin
from django.utils.html import format_html
from .models import Submission, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ['question', 'option', 'answer_text', 'answer_number']
    readonly_fields = ['question', 'option', 'answer_text', 'answer_number']
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj):
        return False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey_link', 'submit_time', 'submit_ip',
                    'duration_seconds', 'answer_count']
    list_filter = ['submit_time', 'survey__title']
    search_fields = ['survey__title', 'submit_ip']
    date_hierarchy = 'submit_time'
    readonly_fields = ['survey', 'submit_time', 'submit_ip',
                       'duration_seconds', 'respondent_info']
    inlines = [AnswerInline]
    list_per_page = 50

    def survey_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:surveys_survey_change', args=[obj.survey.id])
        return format_html('<a href="{}" style="color:#4F46E5">{}</a>', url, obj.survey.title)
    survey_link.short_description = '问卷'

    def answer_count(self, obj):
        return format_html('<b>{}</b> 条', obj.answers.count())
    answer_count.short_description = '答案数'

    def has_add_permission(self, request):
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'submission_id', 'question_preview', 'answer_preview']
    search_fields = ['question__title', 'answer_text', 'submission__survey__title']
    list_select_related = ['question', 'submission__survey']
    list_per_page = 100

    def question_preview(self, obj):
        return f'[{obj.question.survey.title[:20]}] {obj.question.title[:50]}'
    question_preview.short_description = '题目（问卷）'

    def answer_preview(self, obj):
        if obj.option:
            return f'[选项] {obj.option.title[:50]}'
        if obj.answer_text:
            return obj.answer_text[:60]
        if obj.answer_number is not None:
            return str(obj.answer_number)
        return '-'
    answer_preview.short_description = '答案'

    def has_add_permission(self, request):
        return False
