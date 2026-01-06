import pytest
from django.urls import reverse
from myfinances.tests.factories import (
    UserFactory, GroupFactory, StatementFactory, CategoryFactory
)
from myfinances.models import Statements, CategoryList


# ---------------------------------------------------------
# Landing — login required
# ---------------------------------------------------------

@pytest.mark.django_db
def test_landing_page_requires_login(client):
    url = reverse("myfinances:landing")
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_landing_page_logged_in(client):
    user = UserFactory()
    client.force_login(user)

    url = reverse("myfinances:landing")
    response = client.get(url)
    assert response.status_code == 200


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


# ---------------------------------------------------------
# balance_sheet — group-restricted
# ---------------------------------------------------------

@pytest.mark.django_db
def test_balance_sheet_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1, Amount=50)
    stmt2 = StatementFactory(user_group=group2, Amount=999)

    client.force_login(user)

    url = reverse("myfinances:balance_sheet")
    response = client.get(url)

    assert response.status_code == 200
    data = response.context["statements"]

    assert stmt1 in data
    assert stmt2 not in data


# ---------------------------------------------------------
# bulk_update — group-restricted
# ---------------------------------------------------------

@pytest.mark.django_db
def test_bulk_update_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    cat = CategoryFactory(user_group=group1)

    client.force_login(user)

    url = reverse("myfinances:bulk_update")

    # Allowed bulk update
    response = client.post(url, {
        "statement_ids": [stmt1.pk],
        "category_id": cat.pk
    })

    assert response.status_code in (200, 302)
    stmt1.refresh_from_db()
    assert stmt1.Category == cat

    # Denied bulk update (cross-group)
    response = client.post(url, {
        "statement_ids": [stmt2.pk],
        "category_id": cat.pk
    })

    stmt2.refresh_from_db()
    assert stmt2.Category != cat
