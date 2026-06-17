from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Department


class DepartmentSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'parent', 'children', 'full_path',
                  'member_count', 'created_at']

    def get_children(self, obj):
        if obj.children.exists():
            return DepartmentSerializer(obj.children.all(), many=True).data
        return []

    def get_full_path(self, obj):
        return obj.get_full_path()

    def get_member_count(self, obj):
        return obj.get_all_members().count()


class DepartmentFlatSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'parent', 'full_path']

    def get_full_path(self, obj):
        return obj.get_full_path()


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=6, max_length=20)
    password = serializers.CharField(write_only=True, min_length=8, max_length=20)

    def validate_username(self, value):
        import re
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError('账号仅允许字母和数字')
        return value

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'department']

    def create(self, validated_data):
        role = validated_data.get('role', User.ROLE_RESPONDENT)
        if role not in (User.ROLE_CREATOR, User.ROLE_RESPONDENT):
            role = User.ROLE_RESPONDENT
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=role,
            department=validated_data.get('department'),
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError('用户名或密码错误')
        if user.is_banned:
            raise serializers.ValidationError('账号已被封禁')
        return {'user': user}


class UserSerializer(serializers.ModelSerializer):
    role_label = serializers.CharField(source='get_role_display', read_only=True)
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'email', 'employee_id',
                  'phone', 'gender', 'role', 'role_label', 'department', 'department_name',
                  'date_joined', 'is_banned', 'is_super_admin', 'is_creator']
        read_only_fields = ['id', 'username', 'date_joined', 'is_banned',
                            'is_super_admin', 'is_creator']

    def get_department_name(self, obj):
        if obj.department:
            return obj.department.get_full_path()
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    """用户更新个人信息"""
    class Meta:
        model = User
        fields = ['display_name', 'email', 'employee_id', 'phone', 'gender', 'department']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value
