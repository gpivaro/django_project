import pytest
from myfinances.tests.factories import UserFactory, GroupFactory, CategoryFactory


@pytest.mark.django_db
def test_category_is_group_scoped():
    group1 = GroupFactory()
    group2 = GroupFactory()

    user1 = UserFactory(groups=[group1])
    user2 = UserFactory(groups=[group2])

    cat1 = CategoryFactory(name="Food", user_group=group1, owner=user1)
    CategoryFactory(name="Food", user_group=group2, owner=user2)  # allowed

    # user1 should only see group1 categories
    qs1 = CategoryFactory._meta.model.objects.filter(
        user_group__in=user1.groups.all()
    )
    assert list(qs1) == [cat1]
