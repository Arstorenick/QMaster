from django.contrib import admin
from .models import SurveyTemplate, TemplateQuestion, TemplateOption


class TemplateQuestionInline(admin.TabularInline):
    model = TemplateQuestion
    extra = 0


@admin.register(SurveyTemplate)
class SurveyTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'usage_count', 'created_at']
    search_fields = ['title']
    inlines = [TemplateQuestionInline]


@admin.register(TemplateQuestion)
class TemplateQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'title_short']
    search_fields = ['title']

    def title_short(self, obj):
        return obj.title[:60]
    title_short.short_description = '标题'


@admin.register(TemplateOption)
class TemplateOptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_short']
    search_fields = ['title']

    def title_short(self, obj):
        return obj.title[:60]
    title_short.short_description = '选项'
