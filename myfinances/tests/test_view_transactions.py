import pytest
from django.urls import reverse
from myfinances.tests.factories import UserFactory, GroupFactory, StatementFactory


@pytest.mark.django_db
def test_transaction_update_view_group_permission(client):
    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    stmt = StatementFactory(user_group=group)

    url = reverse("myfinances:transactions-update", args=[stmt.id])
    response = client.get(url)

    assert response.status_code == 200  # allowed


@pytest.mark.django_db
def test_transaction_update_view_denied_for_other_group(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory(groups=[group1])
    client.force_login(user)

    stmt = StatementFactory(user_group=group2)

    url = reverse("myfinances:transactions-update", args=[stmt.id])
    response = client.get(url)

    assert response.status_code == 403  # denied
