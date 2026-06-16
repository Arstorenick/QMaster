from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from .models import SurveyTemplate, TemplateQuestion, TemplateOption
from .serializers import (
    TemplateListSerializer, TemplateDetailSerializer,
)
from apps.surveys.models import Survey, Question, Option


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_list(request):
    """模板列表（分页）"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    keyword = request.GET.get('keyword', '')

    qs = SurveyTemplate.objects.all()
    if keyword:
        qs = qs.filter(title__icontains=keyword)

    total = qs.count()
    offset = (page - 1) * page_size
    templates = qs[offset:offset + page_size]

    return Response({
        'total': total,
        'page': page,
        'page_size': page_size,
        'results': TemplateListSerializer(templates, many=True).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def template_detail(request, template_id):
    """模板详情"""
    template = get_object_or_404(SurveyTemplate, id=template_id)
    return Response(TemplateDetailSerializer(template).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_template(request, survey_id):
    """将已有问卷添加到模板库"""
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    if survey.owner != request.user:
        raise PermissionDenied('无权操作此问卷')

    template = SurveyTemplate.objects.create(
        title=survey.title,
        description=survey.description,
        creator=request.user,
    )
    for q in survey.questions.all():
        tq = TemplateQuestion.objects.create(
            template=template,
            type=q.type, title=q.title,
            is_required=q.is_required,
            order=q.order, score=q.score, config=q.config,
        )
        for opt in q.options.all():
            TemplateOption.objects.create(
                question=tq,
                title=opt.title, order=opt.order, score=opt.score,
            )
    return Response(TemplateListSerializer(template).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clone_template(request, template_id):
    """从模板克隆创建问卷"""
    template = get_object_or_404(SurveyTemplate, id=template_id)

    survey = Survey.objects.create(
        title=request.data.get('title', template.title),
        description=template.description,
        owner=request.user,
    )
    for tq in template.questions.all():
        q = Question.objects.create(
            survey=survey,
            type=tq.type, title=tq.title,
            is_required=tq.is_required,
            order=tq.order, score=tq.score, config=tq.config,
        )
        for topt in tq.options.all():
            Option.objects.create(
                question=q,
                title=topt.title, order=topt.order, score=topt.score,
            )

    template.usage_count += 1
    template.save()

    from apps.surveys.serializers import SurveyDetailSerializer
    return Response(SurveyDetailSerializer(survey).data, status=status.HTTP_201_CREATED)
