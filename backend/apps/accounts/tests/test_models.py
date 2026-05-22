import pytest
from django.db import IntegrityError
from apps.accounts.models import User, Role

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_create_user_with_uuid_pk(self):
        user = User.objects.create_user(username='testuser1', email='t1@test.com', password='Abc@123456')
        assert user.id is not None
        assert len(str(user.id)) == 36

    def test_user_default_role_type(self):
        user = User.objects.create_user(username='newuser1', email='n1@test.com', password='Abc@123456')
        assert user.role_type == 'member'

    def test_user_str_returns_username(self):
        user = User.objects.create_user(username='zhangsan', email='zs@test.com', password='Abc@123456')
        assert str(user) == 'zhangsan'

    def test_email_unique_constraint(self):
        User.objects.create_user(username='u1', email='same@test.com', password='Abc@123456')
        with pytest.raises(IntegrityError):
            User.objects.create_user(username='u2', email='same@test.com', password='Abc@123456')

    def test_two_factor_enabled_default(self):
        user = User.objects.create_user(username='u3', email='u3@test.com', password='Abc@123456')
        assert user.two_factor_enabled is False

    def test_role_type_valid_choices(self):
        user = User.objects.create_user(username='u4', email='u4@test.com', password='Abc@123456')
        user.role_type = 'admin'
        user.save()
        user.refresh_from_db()
        assert user.role_type == 'admin'

        user.role_type = 'manager'
        user.save()
        user.refresh_from_db()
        assert user.role_type == 'manager'


class TestRoleModel:
    def test_create_role_with_permissions(self):
        role = Role.objects.create(
            name='测试角色',
            description='测试用',
            permissions={'can_create_task': True},
        )
        assert role.name == '测试角色'
        assert role.permissions['can_create_task'] is True

    def test_role_name_unique(self):
        Role.objects.create(name='unique_role', permissions={})
        with pytest.raises(IntegrityError):
            Role.objects.create(name='unique_role', permissions={})
