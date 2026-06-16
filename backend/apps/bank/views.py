from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import QuestionBankItem
from apps.surveys.models import Survey, Question, Option


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bank_list(request):
    """题库列表"""
    category = request.GET.get('category', '')
    keyword = request.GET.get('keyword', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    qs = QuestionBankItem.objects.all()
    if category:
        qs = qs.filter(category=category)
    if keyword:
        qs = qs.filter(title__icontains=keyword)

    total = qs.count()
    offset = (page - 1) * page_size
    items = qs[offset:offset + page_size]

    return Response({
        'total': total,
        'page': page,
        'page_size': page_size,
        'results': [
            {
                'id': item.id,
                'category': item.category,
                'label': item.label,
                'question_type': item.question_type,
                'title': item.title,
                'options_data': item.options_data,
                'config': item.config,
            } for item in items
        ],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bank_import(request, item_id, survey_id):
    """从题库导入题目到问卷"""
    item = get_object_or_404(QuestionBankItem, id=item_id)
    survey = get_object_or_404(Survey, id=survey_id, is_deleted=False)
    if survey.owner != request.user:
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('无权操作此问卷')

    last = survey.questions.order_by('-order').first()
    order = (last.order + 1) if last else 0

    question = Question.objects.create(
        survey=survey,
        type=item.question_type,
        title=item.title,
        order=order,
        config=item.config,
    )
    for i, opt_data in enumerate(item.options_data):
        Option.objects.create(
            question=question,
            title=opt_data.get('title', ''),
            order=i,
            score=opt_data.get('score', 0),
        )

    from apps.surveys.serializers import QuestionSerializer
    return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
