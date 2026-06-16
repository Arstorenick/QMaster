from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Survey, Question, Option


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['type', 'title', 'is_required', 'order']
    show_change_link = True


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'status_badge', 'question_count',
                    'submission_count', 'created_at', 'view_stats']
    list_filter = ['status', 'created_at', 'owner']
    search_fields = ['title', 'owner__username', 'description']
    date_hierarchy = 'created_at'
    inlines = [QuestionInline]
    readonly_fields = ['question_count', 'submission_count', 'owner']
    list_per_page = 20

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'owner', 'status')
        }),
        ('样式配置', {
            'fields': ('style',),
            'classes': ('collapse',),
        }),
        ('统计数据', {
            'fields': ('question_count', 'submission_count', 'created_at', 'updated_at'),
        }),
    )

    def status_badge(self, obj):
        colors = {0: '#F59E0B', 1: '#10B981', 2: '#EF4444'}
        labels = {0: '草稿', 1: '已发布', 2: '已关闭'}
        return format_html(
            '<span style="display:inline-block;padding:2px 10px;border-radius:12px;'
            'background:{};color:#fff;font-size:12px;font-weight:500">{}</span>',
            colors.get(obj.status, '#999'), labels.get(obj.status, '未知')
        )
    status_badge.short_description = '状态'

    def question_count(self, obj):
        count = obj.questions.count()
        return format_html('<b>{}</b> 题', count)
    question_count.short_description = '题目数'

    def submission_count(self, obj):
        return format_html('<b>{}</b> 份', obj.submissions.count())
    submission_count.short_description = '提交数'

    def view_stats(self, obj):
        return format_html(
            '<a href="#" onclick="window.open(\'/display/{}\');return false" '
            'style="color:#4F46E5">📋 预览</a>', obj.id
        )
    view_stats.short_description = '操作'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'title_short', 'survey_link', 'is_required', 'order']
    list_filter = ['type', 'is_required', 'survey__status']
    search_fields = ['title', 'survey__title']
    list_select_related = ['survey']

    def title_short(self, obj):
        return obj.title[:80]
    title_short.short_description = '标题'

    def survey_link(self, obj):
        url = reverse('admin:surveys_survey_change', args=[obj.survey.id])
        return format_html('<a href="{}" style="color:#4F46E5">{}</a>', url, obj.survey.title[:50])
    survey_link.short_description = '所属问卷'


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_short', 'question_link', 'order', 'score']
    search_fields = ['title', 'question__title']
    list_select_related = ['question__survey']

    def title_short(self, obj):
        return obj.title[:80]
    title_short.short_description = '选项'

    def question_link(self, obj):
        url = reverse('admin:surveys_question_change', args=[obj.question.id])
        return format_html(
            '<a href="{}" style="color:#4F46E5">{} ({})</a>',
            url, obj.question.title[:50], obj.question.survey.title[:30]
        )
    question_link.short_description = '所属题目'
