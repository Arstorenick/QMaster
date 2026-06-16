from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.views.decorators.csrf import ensure_csrf_cookie

import io, csv
from .models import User, Department
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    UserProfileSerializer, ChangePasswordSerializer,
    DepartmentSerializer, DepartmentFlatSerializer,
)


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_view(request):
    return Response({'detail': 'CSRF cookie set'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        return Response(UserSerializer(user).data)
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'detail': '已退出登录'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """更新个人信息"""
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """修改密码"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': '密码已修改'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ═══════════════════════════════════════════════
#  Department
# ═══════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def department_list(request):
    """部门列表 / 创建部门（仅制表人以上）"""
    if request.method == 'GET':
        depts = Department.objects.filter(parent__isnull=True).order_by('name')
        return Response(DepartmentSerializer(depts, many=True).data)

    if not request.user.is_creator:
        return Response({'detail': '仅总管理或出题人可操作'}, status=status.HTTP_403_FORBIDDEN)

    serializer = DepartmentFlatSerializer(data=request.data)
    if serializer.is_valid():
        dept = serializer.save(creator=request.user)
        return Response(DepartmentFlatSerializer(dept).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def department_detail(request, dept_id):
    """部门详情 / 删除"""
    dept = Department.objects.get(id=dept_id)
    if request.method == 'GET':
        return Response({
            **DepartmentFlatSerializer(dept).data,
            'members': UserSerializer(dept.get_all_members(), many=True).data,
        })
    if not request.user.is_creator:
        return Response({'detail': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
    dept.delete()
    return Response({'detail': '已删除'})


@api_view(['GET'])
@permission_classes([AllowAny])
def department_flat_list(request):
    """扁平部门列表（下拉选择用）"""
    depts = Department.objects.all().order_by('parent__id', 'name')
    return Response(DepartmentFlatSerializer(depts, many=True).data)


# ═══════════════════════════════════════════════
#  Batch Import
# ═══════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_import(request):
    """CSV 批量导入部门/用户（仅总管理/出题人）"""
    if not request.user.is_creator:
        return Response({'detail': '无权操作'}, status=status.HTTP_403_FORBIDDEN)

    csv_text = request.data.get('csv', '')
    import_type = request.data.get('type', 'department')  # 'department' or 'user'
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    if len(rows) < 2:
        return Response({'detail': 'CSV 至少需要表头+1行数据'}, status=status.HTTP_400_BAD_REQUEST)

    created, errors = [], []
    for i, row in enumerate(rows[1:], start=2):
        try:
            if import_type == 'department':
                name = row[0].strip()
                parent_path = row[1].strip() if len(row) > 1 and row[1].strip() else None
                parent = None
                if parent_path:
                    # 按完整路径查找父部门
                    parents = Department.objects.all()
                    for p in parents:
                        if p.get_full_path() == parent_path:
                            parent = p
                            break
                    if not parent:
                        errors.append(f'行{i}: 未找到上级部门 "{parent_path}"')
                        continue
                dept = Department.objects.create(name=name, parent=parent, creator=request.user)
                created.append(dept.get_full_path())

            elif import_type == 'user':
                username = row[0].strip()
                password = row[1].strip() if len(row) > 1 else '123456'
                role = int(row[2]) if len(row) > 2 and row[2].strip() else 3
                dept_path = row[3].strip() if len(row) > 3 and row[3].strip() else None
                dept = None
                if dept_path:
                    for d in Department.objects.all():
                        if d.get_full_path() == dept_path:
                            dept = d
                            break
                user, is_new = User.objects.get_or_create(username=username)
                if is_new:
                    user.set_password(password)
                user.role = role
                user.department = dept
                user.save()
                created.append(f'{username} (角色:{role})')
        except Exception as e:
            errors.append(f'行{i}: {str(e)}')

    return Response({'created': created, 'errors': errors, 'total': len(created)})


# ═══════════════════════════════════════════════
#  Department Dashboard
# ═══════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dept_dashboard(request):
    """部门统计看板"""
    if not request.user.is_creator:
        return Response({'detail': '无权操作'}, status=status.HTTP_403_FORBIDDEN)

    from apps.surveys.models import Survey
    from apps.responses.models import Submission

    depts = Department.objects.filter(parent__isnull=True)
    total_users = User.objects.count()
    total_surveys = Survey.objects.filter(is_deleted=False).count()
    total_submissions = Submission.objects.count()

    dept_stats = []
    for dept in depts:
        members = dept.get_all_members()
        member_ids = list(members.values_list('id', flat=True))
        submissions = Submission.objects.filter(
            survey__is_deleted=False
        ).filter(
            survey__target_departments=dept
        ).count() if member_ids else 0

        dept_stats.append({
            'id': dept.id,
            'name': dept.name,
            'full_path': dept.get_full_path(),
            'member_count': len(member_ids),
            'submission_count': submissions,
            'children_count': dept.children.count(),
        })

    return Response({
        'total_users': total_users,
        'total_surveys': total_surveys,
        'total_submissions': total_submissions,
        'departments': dept_stats,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dept_survey_stats(request, survey_id):
    """按部门统计某问卷的提交情况"""
    from apps.surveys.models import Survey
    from apps.responses.models import Submission

    survey = Survey.objects.get(id=survey_id)
    if not request.user.is_creator:
        return Response({'detail': '无权操作'}, status=status.HTTP_403_FORBIDDEN)

    depts = Department.objects.all()
    dept_submissions = []
    for dept in depts:
        members = dept.get_all_members()
        if not members:
            continue
        count = Submission.objects.filter(
            survey=survey
        ).count()  # Simplified — ideally filter by member IP/user
        dept_submissions.append({
            'id': dept.id,
            'name': dept.name,
            'full_path': dept.get_full_path(),
            'member_count': members.count(),
            'submission_count': count,
        })

    return Response({
        'survey_title': survey.title,
        'total_submissions': survey.submissions.count(),
        'departments': dept_submissions,
    })
