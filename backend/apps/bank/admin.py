from django.contrib import admin
from .models import QuestionBankItem


@admin.register(QuestionBankItem)
class QuestionBankItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'label', 'question_type', 'title_short']
    list_filter = ['category', 'question_type']
    search_fields = ['title', 'label']

    def title_short(self, obj):
        return obj.title[:60]
    title_short.short_description = '标题'
