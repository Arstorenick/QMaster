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
                  'managed_department', 'date_joined', 'is_banned', 'is_super_admin', 'is_creator']
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

    def validate_department(self, value):
        request = self.context.get('request')
        if request and request.user.is_creator:
            raise serializers.ValidationError('管理员不能修改自己的所属部门')
        return value


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """管理员编辑用户信息"""
    class Meta:
        model = User
        fields = ['display_name', 'employee_id', 'phone', 'department', 'role', 'managed_department']

    def validate_managed_department(self, value):
        request = self.context.get('request')
        if not value or not request:
            return value
        user = request.user
        if user.is_super_admin:
            return value
        # 管理员只能设为自己所属部门或子部门
        if user.department:
            allowed = user.department.get_descendant_ids()
            if value.id not in allowed:
                raise serializers.ValidationError('只能设为所辖范围内的部门')
        else:
            raise serializers.ValidationError('无权设置管理部门')
        return value

    def validate_department(self, value):
        request = self.context.get('request')
        if request and self.instance and self.instance.id == request.user.id:
            raise serializers.ValidationError('不能修改自己的所属部门')
        return value

    def validate_role(self, value):
        request = self.context.get('request')
        if request and not request.user.is_creator:
            raise serializers.ValidationError('无权修改角色')
        if request and self.instance and self.instance.id == request.user.id:
            raise serializers.ValidationError('不能修改自己的角色')
        if value not in (2, 3):
            raise serializers.ValidationError('角色无效，仅可设为管理员(2)或用户(3)')
        return value

    def validate_managed_department(self, value):
        request = self.context.get('request')
        if request and self.instance and self.instance.id == request.user.id:
            raise serializers.ValidationError('不能修改自己的管理部门')
        if not value or not request:
            return value
        user = request.user
        if user.is_super_admin:
            return value
        if user.department:
            allowed = user.department.get_descendant_ids()
            if value.id not in allowed:
                raise serializers.ValidationError('只能设为所辖范围内的部门')
        else:
            raise serializers.ValidationError('无权设置管理部门')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value
