import pytest
from django.urls import reverse
from myfinances.tests.factories import UserFactory, GroupFactory, CategoryFactory


@pytest.mark.django_db
def test_category_list_view_group_filter(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory(groups=[group1])
    client.force_login(user)

    cat1 = CategoryFactory(user_group=group1, owner=user)
    CategoryFactory(user_group=group2)  # should not appear

    url = reverse("myfinances:categories-list")
    response = client.get(url)

    categories = response.context["categories_list"]
    assert list(categories) == [cat1]
