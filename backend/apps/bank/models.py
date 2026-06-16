from django.db import models


class QuestionBankItem(models.Model):
    """题库条目"""
    CATEGORY_CHOICES = [
        ('major', '专业'),
        ('school', '院校'),
        ('industry', '行业'),
        ('occupation', '职业'),
        ('region', '行政区划'),
        ('common', '常用'),
    ]

    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    label = models.CharField('标签/关键词', max_length=200, db_index=True)
    question_type = models.CharField('题型', max_length=30)
    title = models.CharField('题目标题', max_length=1000)
    options_data = models.JSONField('选项数据', default=list, blank=True)
    config = models.JSONField('扩展配置', default=dict, blank=True)

    class Meta:
        db_table = 'question_bank'
        ordering = ['category', 'label']
        verbose_name = '题库'
        verbose_name_plural = '题库'

    def __str__(self):
        return f'[{self.get_category_display()}] {self.title[:50]}'
