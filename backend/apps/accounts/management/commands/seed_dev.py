from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = '创建开发测试用户'

    def handle(self, *args, **options):
        if not User.objects.filter(username='test').exists():
            User.objects.create_user(
                username='test',
                email='test@example.com',
                password='123456',
                role_type='admin',
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS('测试用户已创建: test / 123456'))
        else:
            self.stdout.write(self.style.WARNING('测试用户已存在，跳过'))
