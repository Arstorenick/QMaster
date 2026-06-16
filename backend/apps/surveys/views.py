from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Survey, Question, Option
from .serializers import (
    SurveyListSerializer, SurveyDetailSerializer,
    QuestionSerializer, OptionSerializer,
    StyleUpdateSerializer, ReorderSerializer,
)


def require_creator(user):
    """要求 1级总管理 或 2级出题人"""
    if not user.is_creator:
        raise PermissionDenied('仅总管理或出题人可操作，当前角色无权限')


def check_owner(user, survey):
    """检查用户是否为问卷所有者"""
    require_creator(user)
    if survey.owner != user:
        raise PermissionDenied('无权操作此问卷')


# ══════════════════════════════════════════════════════════
#  Survey CRUD
# ══════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def survey_list(request):
    """我的问卷列表"""
    require_creator(request.user)
    surveys = Survey.objects.filter(
        owner=request.user, is_deleted=False
    ).order_by('-updated_at')
    return Response(SurveyListSerializer(surveys, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def survey_create(request):
    """创建问卷"""
    require_creator(request.user)
    serializer = SurveyListSerializer(data=request.data)
    if serializer.is_valid():
        survey = serializer.save(owner=request.user)
        return Response(SurveyDetailSerializer(survey).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def survey_detail(request, survey_id):
    """问卷详情 / 更新 / 软删除"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)

    if request.method == 'GET':
        return Response(SurveyDetailSerializer(survey).data)

    if request.method == 'PUT':
        serializer = SurveyListSerializer(survey, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(SurveyDetailSerializer(survey).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        survey.is_deleted = True
        survey.save()
        return Response({'detail': '问卷已删除'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def survey_publish(request, survey_id):
    """发布 / 取消发布 / 关闭问卷。发布时自动推送到管理员所属部门及子部门"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)

    new_status = request.data.get('status')
    if new_status not in [0, 1, 2]:
        return Response({'detail': '状态值无效'}, status=status.HTTP_400_BAD_REQUEST)

    survey.status = new_status

    # 发布时记录时间 + 设置目标部门
    if new_status == 1:
        from django.utils import timezone
        survey.published_at = timezone.now()
        target_ids = request.data.get('target_departments', None)
        from apps.users.models import Department
        if target_ids is not None:
            # 管理员手动指定了目标部门
            target_depts = Department.objects.filter(id__in=target_ids)
            survey.target_departments.set(target_depts)
        elif request.user.department:
            # 自动推送到管理员所属部门及所有子部门
            dept_ids = request.user.department.get_descendant_ids()
            target_depts = Department.objects.filter(id__in=dept_ids)
            survey.target_departments.set(target_depts)

    survey.save()
    return Response({'status': survey.status, 'detail': '状态已更新'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def survey_copy(request, survey_id):
    """复制问卷（用于停止收集后修改再发布）"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)

    new_survey = Survey.objects.create(
        title=request.data.get('title', survey.title + ' (副本)'),
        description=survey.description,
        owner=request.user,
        status=0,
        style=survey.style.copy() if survey.style else {},
    )
    for q in survey.questions.all():
        new_q = Question.objects.create(
            survey=new_survey,
            type=q.type, title=q.title, is_required=q.is_required,
            order=q.order, score=q.score, config=q.config.copy() if q.config else {},
        )
        for opt in q.options.all():
            Option.objects.create(
                question=new_q, title=opt.title, order=opt.order,
                score=opt.score, image=opt.image,
            )
    return Response(SurveyDetailSerializer(new_survey).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def survey_style(request, survey_id):
    """更新样式配置"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)

    if survey.style is None:
        survey.style = {}
    survey.style.update(request.data.get('style', {}))
    survey.save()
    return Response({'style': survey.style})


# ══════════════════════════════════════════════════════════
#  Public Survey (for respondents)
# ══════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_tasks(request):
    """返回推送给当前用户部门的问卷，含提交状态"""
    user = request.user
    if not user.department:
        return Response([])
    dept_ids = user.department.get_descendant_ids()
    surveys = Survey.objects.filter(
        status=1, is_deleted=False,
        target_departments__id__in=dept_ids
    ).distinct().order_by('-updated_at')

    from apps.responses.models import Submission
    data = []
    for s in surveys:
        item = SurveyListSerializer(s).data
        item['submitted'] = Submission.objects.filter(survey=s).exists()  # Simplified: check if any submission exists
        data.append(item)

    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def public_list(request):
    """公开问卷列表（已发布且未删除）"""
    surveys = Survey.objects.filter(status=1, is_deleted=False).order_by('-updated_at')
    return Response(SurveyListSerializer(surveys, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def survey_public(request, survey_id):
    """获取问卷（已发布公开可见，所有者可预览未发布问卷）"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    if survey.status != 1 and (not request.user.is_authenticated or survey.owner != request.user):
        return Response({'detail': '问卷未发布'}, status=404)
    return Response(SurveyDetailSerializer(survey).data)


# ══════════════════════════════════════════════════════════
#  Question CRUD
# ══════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def question_list(request, survey_id):
    """题目列表 / 创建题目"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)

    if request.method == 'GET':
        questions = survey.questions.all().order_by('order')
        return Response(QuestionSerializer(questions, many=True).data)

    if request.method == 'POST':
        last = survey.questions.order_by('-order').first()
        request.data.setdefault('order', (last.order + 1) if last else 0)
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save(survey=survey)
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def question_detail(request, survey_id, question_id):
    """题目详情 / 更新 / 删除"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)
    question = get_object_or_404(Question, id=question_id, survey=survey)

    if request.method == 'GET':
        return Response(QuestionSerializer(question).data)

    if request.method == 'PUT':
        serializer = QuestionSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(QuestionSerializer(question).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        question.delete()
        return Response({'detail': '题目已删除'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def question_reorder(request, survey_id):
    """拖拽排序"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)

    question_ids = request.data.get('question_ids', [])
    for order, qid in enumerate(question_ids):
        Question.objects.filter(id=qid, survey=survey).update(order=order)

    return Response({'detail': '排序已更新'})


# ══════════════════════════════════════════════════════════
#  Option CRUD
# ══════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def option_create(request, survey_id, question_id):
    """为题目添加选项"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)
    question = get_object_or_404(Question, id=question_id, survey=survey)

    last = question.options.order_by('-order').first()
    request.data.setdefault('order', (last.order + 1) if last else 0)
    serializer = OptionSerializer(data=request.data)
    if serializer.is_valid():
        option = serializer.save(question=question)
        return Response(OptionSerializer(option).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def option_detail(request, survey_id, question_id, option_id):
    """更新 / 删除选项"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    check_owner(request.user, survey)
    question = get_object_or_404(Question, id=question_id, survey=survey)
    option = get_object_or_404(Option, id=option_id, question=question)

    if request.method == 'PUT':
        serializer = OptionSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        option.delete()
        return Response({'detail': '选项已删除'})
