from django.db import models
from apps.surveys.models import Survey, Question, Option


class Submission(models.Model):
    """提交记录"""
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE,
        related_name='submissions', verbose_name='问卷'
    )
    respondent_info = models.JSONField('答卷人信息', default=dict, blank=True)
    submit_time = models.DateTimeField('提交时间', auto_now_add=True)
    submit_ip = models.GenericIPAddressField('提交 IP')
    duration_seconds = models.PositiveIntegerField('填写用时(秒)', default=0)

    class Meta:
        db_table = 'submissions'
        ordering = ['-submit_time']
        verbose_name = '提交记录'
        verbose_name_plural = '提交记录'

    def __str__(self):
        return f'{self.survey.title} - {self.submit_ip} - {self.submit_time}'


class Answer(models.Model):
    """回答"""
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE,
        related_name='answers', verbose_name='提交'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='answers', verbose_name='题目'
    )
    option = models.ForeignKey(
        Option, on_delete=models.CASCADE,
        null=True, blank=True, verbose_name='选项'
    )
    answer_text = models.TextField('文本答案', null=True, blank=True)
    answer_number = models.FloatField('数值答案', null=True, blank=True)
    answer_file = models.FileField('文件答案', upload_to='answers/', null=True, blank=True)
    answer_json = models.JSONField('JSON 答案', null=True, blank=True)

    class Meta:
        db_table = 'answers'
        indexes = [
            models.Index(fields=['question', 'option']),
        ]
        verbose_name = '回答'
        verbose_name_plural = '回答'

    def __str__(self):
        return f'{self.question.title[:30]} → {self.answer_text or self.option or ""}'[:60]
