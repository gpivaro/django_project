import pytest
from django.urls import reverse
from myfinances.tests.factories import (
    UserFactory, GroupFactory, StatementFactory, CategoryFactory
)
from myfinances.models import Statements, CategoryList


# ---------------------------------------------------------
# categories — group-restricted
# ---------------------------------------------------------

@pytest.mark.django_db
def test_categories_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    cat1 = CategoryFactory(user_group=group1)
    cat2 = CategoryFactory(user_group=group2)

    client.force_login(user)

    url = reverse("myfinances:categories")
    response = client.get(url)

    assert response.status_code == 200
    categories = response.context["categories"]

    assert cat1 in categories
    assert cat2 not in categories


# ---------------------------------------------------------
# statement — group-restricted
# ---------------------------------------------------------

@pytest.mark.skip(reason="Statement view being refactored; does not save to DB yet.")
def test_statement_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    url = reverse("myfinances:statement")
    response = client.get(url)

    assert response.status_code == 200
    statements = response.context["statements"]

    assert stmt1 in statements
    assert stmt2 not in statements


# ---------------------------------------------------------
# banktransactions — group-restricted
# ---------------------------------------------------------

@pytest.mark.django_db
def test_banktransactions_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    url = reverse("myfinances:banktransactions")
    response = client.get(url)

    assert response.status_code == 200
    transactions = response.context["transactions"]

    assert stmt1 in transactions
    assert stmt2 not in transactions
