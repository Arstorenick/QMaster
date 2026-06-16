from django.db import models
from django.conf import settings


class SurveyTemplate(models.Model):
    """问卷模板"""
    title = models.CharField('标题', max_length=200)
    description = models.TextField('说明', blank=True, default='')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='创建者'
    )
    usage_count = models.PositiveIntegerField('使用次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'survey_templates'
        ordering = ['-usage_count']
        verbose_name = '问卷模板'
        verbose_name_plural = '问卷模板'

    def __str__(self):
        return self.title


class TemplateQuestion(models.Model):
    """模板题目"""
    template = models.ForeignKey(
        SurveyTemplate, on_delete=models.CASCADE,
        related_name='questions', verbose_name='所属模板'
    )
    type = models.CharField('题型', max_length=30)
    title = models.CharField('标题', max_length=1000)
    is_required = models.BooleanField('必填', default=True)
    order = models.IntegerField('排序', default=0)
    score = models.IntegerField('分数', default=0)
    config = models.JSONField('扩展配置', default=dict, blank=True)

    class Meta:
        db_table = 'template_questions'
        ordering = ['order']
        verbose_name = '模板题目'

    def __str__(self):
        return self.title[:50]


class TemplateOption(models.Model):
    """模板选项"""
    question = models.ForeignKey(
        TemplateQuestion, on_delete=models.CASCADE,
        related_name='options', verbose_name='所属题目'
    )
    title = models.CharField('选项名', max_length=500)
    order = models.IntegerField('排序', default=0)
    score = models.IntegerField('分值', default=0)

    class Meta:
        db_table = 'template_options'
        ordering = ['order']
        verbose_name = '模板选项'

    def __str__(self):
        return self.title[:50]
