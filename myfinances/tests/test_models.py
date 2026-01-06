import pytest
from django.db import IntegrityError
from myfinances.tests.factories import GroupFactory, UserFactory, CategoryFactory


@pytest.mark.django_db
def test_category_unique_per_group():
    group = GroupFactory()
    user = UserFactory(groups=[group])

    CategoryFactory(name="Rent", user_group=group, owner=user)

    with pytest.raises(IntegrityError):
        CategoryFactory(name="Rent", user_group=group, owner=user)
