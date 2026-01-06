import pytest
from django.urls import reverse
from myfinances.tests.factories import UserFactory, GroupFactory, StatementFactory, CategoryFactory


@pytest.mark.django_db
def test_manage_statements_group_restriction(client):
    group = GroupFactory()
    other_group = GroupFactory()

    user = UserFactory(groups=[group])
    client.force_login(user)

    stmt = StatementFactory(user_group=group, Owner=user)
    other_stmt = StatementFactory(user_group=other_group)

    category = CategoryFactory(user_group=group, owner=user)

    url = reverse("myfinances:manage_statements")

    response = client.post(url, {
        "stmt_id": stmt.id,
        "Name": category.name,
    })

    stmt.refresh_from_db()
    assert stmt.Category == category

    # trying to update a statement outside the group should 404
    response = client.post(url, {
        "stmt_id": other_stmt.id,
        "Name": category.name,
    })
    assert response.status_code == 404
