import pytest
from django.urls import reverse
from myfinances.tests.factories import (
    UserFactory, GroupFactory, StatementFactory, CategoryFactory
)
from myfinances.models import Statements


# ---------------------------------------------------------
# manage_statements — group-restricted access
# ---------------------------------------------------------

@pytest.mark.django_db
def test_manage_statements_group_restriction(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    url = reverse("myfinances:manage_statements")
    response = client.get(url)

    assert response.status_code == 200
    statements = response.context["statements"]

    # Only group1 statements should appear
    assert stmt1 in statements
    assert stmt2 not in statements


# ---------------------------------------------------------
# manage_items — group-restricted access
# ---------------------------------------------------------

@pytest.mark.skip(reason="Temporarily skipping while refactoring manage_statements view.")
def test_manage_items_group_restriction(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    url = reverse("myfinances:manage_items")
    response = client.get(url)

    assert response.status_code == 200
    items = response.context["items"]

    # Only items from group1 statements should appear
    assert stmt1 in items
    assert stmt2 not in items


# ---------------------------------------------------------
# manage_statements — category filtering
# ---------------------------------------------------------

@pytest.mark.django_db
def test_manage_statements_category_filter(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    cat_food = CategoryFactory(user_group=group, label="Food")
    cat_util = CategoryFactory(user_group=group, label="Utilities")

    stmt1 = StatementFactory(user_group=group, Category=cat_food)
    stmt2 = StatementFactory(user_group=group, Category=cat_util)

    client.force_login(user)

    url = reverse("myfinances:manage_statements") + \
        f"?category={cat_food.label}"
    response = client.get(url)

    assert response.status_code == 200
    statements = response.context["statements"]

    assert stmt1 in statements
    assert stmt2 not in statements


# ---------------------------------------------------------
# manage_statements — updating a statement (group-restricted)
# ---------------------------------------------------------

@pytest.mark.django_db
def test_manage_statements_update_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    # Allowed update
    url = reverse("myfinances:manage_statements")
    response = client.post(url, {
        "statement_id": stmt1.pk,
        "Description": "Updated description",
        "Amount": stmt1.Amount,
        "Type": stmt1.Type,
        "Balance": stmt1.Balance,
        "Acct_Info": stmt1.Acct_Info,
        "Posting_Date": stmt1.Posting_Date,
    })

    assert response.status_code in (200, 302)
    stmt1.refresh_from_db()
    assert stmt1.Description == "Updated description"

    # Denied update (should not modify stmt2)
    response = client.post(url, {
        "statement_id": stmt2.pk,
        "Description": "Hacked",
        "Amount": stmt2.Amount,
        "Type": stmt2.Type,
        "Balance": stmt2.Balance,
        "Acct_Info": stmt2.Acct_Info,
        "Posting_Date": stmt2.Posting_Date,
    })

    stmt2.refresh_from_db()
    assert stmt2.Description != "Hacked"
