from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    """部门（多级树形结构）"""
    name = models.CharField('部门名称', max_length=100)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name='上级部门'
    )
    creator = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='created_departments',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'departments'
        verbose_name = '部门'
        verbose_name_plural = '部门列表'
        ordering = ['parent__id', 'name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} > {self.name}'
        return self.name

    def get_full_path(self):
        """返回完整路径，如 '沈阳公司 > 和平区分公司'"""
        if self.parent:
            return f'{self.parent.get_full_path()} > {self.name}'
        return self.name

    def get_all_members(self):
        """获取该部门及子部门所有成员"""
        from django.db.models import Q
        dept_ids = [self.id]
        for child in self.children.all():
            dept_ids.extend(child.get_descendant_ids())
        return User.objects.filter(department_id__in=dept_ids)

    def get_descendant_ids(self):
        """递归获取所有子孙部门 ID"""
        ids = [self.id]
        for child in self.children.all():
            ids.extend(child.get_descendant_ids())
        return ids


class User(AbstractUser):
    """扩展 Django 内置 User"""
    ROLE_SUPER_ADMIN = 1
    ROLE_CREATOR = 2
    ROLE_RESPONDENT = 3
    ROLE_DEPT_HEAD = 4
    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, '总管理'),
        (ROLE_CREATOR, '管理员'),
        (ROLE_RESPONDENT, '用户'),
        (ROLE_DEPT_HEAD, '部门负责人'),
    ]

    role = models.SmallIntegerField('角色', choices=ROLE_CHOICES, default=ROLE_RESPONDENT)
    is_banned = models.BooleanField('封禁', default=False)
    display_name = models.CharField('姓名', max_length=50, blank=True, default='')
    employee_id = models.CharField('工号', max_length=50, blank=True, default='')
    phone = models.CharField('联系方式', max_length=20, blank=True, default='')
    gender = models.CharField('性别', max_length=10, blank=True, default='',
                              choices=[('', '未选择'), ('male', '男'), ('female', '女')])
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='members', verbose_name='所属部门'
    )
    managed_department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managers', verbose_name='管理的部门'
    )

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户列表'

    def __str__(self):
        if self.department:
            return f'{self.username} [{self.get_role_display()}] @ {self.department.get_full_path()}'
        return f'{self.username} [{self.get_role_display()}]'

    @property
    def is_super_admin(self):
        return self.role == self.ROLE_SUPER_ADMIN or self.is_superuser

    @property
    def is_creator(self):
        return self.role in (self.ROLE_SUPER_ADMIN, self.ROLE_CREATOR)

    @property
    def is_dept_head(self):
        return self.role == self.ROLE_DEPT_HEAD

    @property
    def is_respondent(self):
        return self.role == self.ROLE_RESPONDENT
