import pytest
from apps.accounts.models import User


@pytest.fixture
def django_user(db):
    return User.objects.create_user(
        username='testuser', email='test@example.com', password='Test@123456'
    )
