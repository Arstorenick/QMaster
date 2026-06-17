from django.db import models
from django.conf import settings


class Survey(models.Model):
    """问卷"""
    STATUS_CHOICES = [(0, '草稿'), (1, '已发布'), (2, '已关闭')]

    title = models.CharField('标题', max_length=200)
    description = models.TextField('说明', blank=True, default='')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='surveys', verbose_name='创建者'
    )
    status = models.SmallIntegerField('状态', choices=STATUS_CHOICES, default=0)
    is_deleted = models.BooleanField('已删除', default=False)
    style = models.JSONField('样式配置', default=dict, blank=True)
    scoring_enabled = models.BooleanField('启用评分', default=False)
    target_departments = models.ManyToManyField(
        'users.Department', blank=True, related_name='targeted_surveys',
        verbose_name='定向部门'
    )
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'surveys'
        ordering = ['-updated_at']
        verbose_name = '问卷'
        verbose_name_plural = '问卷列表'

    def __str__(self):
        return self.title


class Question(models.Model):
    """题目 — 支持 40+ 题型，扩展配置存 JSON"""
    TYPE_CHOICES = [
        # MVP 阶段
        ('radio', '单选题'),
        ('checkbox', '多选题'),
        ('text', '填空题'),
        ('textarea', '多行填空题'),
        ('multi_text', '多项填空题'),
        ('dropdown', '下拉单选题'),
        ('rating', '评分题'),
        ('ranking', '排序题'),
        ('date', '日期题'),
        ('time', '时间题'),
        ('file_upload', '文件上传题'),
        ('page_break', '分页'),
        ('section_break', '分段'),
        ('scale', '量表题'),
        ('slider', '滑块题'),
        ('image_radio', '图片单选题'),
        ('image_checkbox', '图片多选题'),
        # 进阶阶段
        ('cascade', '级联题'),
        ('signature', '签名题'),
        ('location', '定位题'),
        ('matrix_radio', '矩阵单选题'),
        ('matrix_checkbox', '矩阵多选题'),
        ('matrix_rating', '矩阵评分题'),
        ('matrix_text', '矩阵填空题'),
        ('matrix_scale', '矩阵量表题'),
        ('matrix_slider', '矩阵滑块题'),
        ('matrix_numeric', '矩阵数值题'),
        ('divider', '分割线'),
        ('image_upload', '图片上传'),
        ('image_carousel', '图片轮播'),
        # 完整阶段
        ('screening', '甄别题'),
        ('drawing', '绘图题'),
        ('map', '地图组件'),
        ('matrix_dropdown', '矩阵下拉题'),
        ('matrix_combo', '矩阵组合题'),
        ('matrix_auto_inc', '矩阵自增题'),
    ]

    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE,
        related_name='questions', verbose_name='所属问卷'
    )
    type = models.CharField('题目类型', max_length=30, choices=TYPE_CHOICES)
    title = models.CharField('题目标题', max_length=1000, blank=True, default='')
    is_required = models.BooleanField('必填', default=True)
    order = models.IntegerField('排序', default=0, db_index=True)
    score = models.IntegerField('题目分数', default=0)
    config = models.JSONField('扩展配置', default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questions'
        ordering = ['order']
        verbose_name = '题目'
        verbose_name_plural = '题目列表'

    def __str__(self):
        return f'[{self.get_type_display()}] {self.title[:50]}'


class Option(models.Model):
    """选项"""
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='options', verbose_name='所属题目'
    )
    title = models.CharField('选项名', max_length=1000, blank=True, default='')
    order = models.IntegerField('排序', default=0)
    score = models.IntegerField('选项分值', default=0)
    image = models.ImageField('选项图片', upload_to='options/', null=True, blank=True)

    class Meta:
        db_table = 'options'
        ordering = ['order']
        verbose_name = '选项'
        verbose_name_plural = '选项列表'

    def __str__(self):
        return self.title[:50]
