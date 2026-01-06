import pytest
from django.urls import reverse
from myfinances.tests.factories import (
    UserFactory, GroupFactory, StatementFactory
)
from myfinances.models import Statements


# ---------------------------------------------------------
# TransactionsListView — group-restricted queryset
# ---------------------------------------------------------

@pytest.mark.django_db
def test_transactions_list_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    url = reverse("myfinances:transactions-list")
    response = client.get(url)

    assert response.status_code == 200
    transactions = response.context["transactions"]

    assert stmt1 in transactions
    assert stmt2 not in transactions


# ---------------------------------------------------------
# TransactionsDetailView — group-restricted access
# ---------------------------------------------------------

@pytest.mark.django_db
def test_transactions_detail_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    # Allowed
    url = reverse("myfinances:transactions-detail", args=[stmt1.pk])
    response = client.get(url)
    assert response.status_code == 200

    # Denied
    url = reverse("myfinances:transactions-detail", args=[stmt2.pk])
    response = client.get(url)
    assert response.status_code == 404


# ---------------------------------------------------------
# TransactionsUpdateView — group-restricted update
# ---------------------------------------------------------

@pytest.mark.django_db
def test_transaction_update_view_group_permission(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    # Allowed update
    url = reverse("myfinances:transactions-update", args=[stmt1.pk])
    response = client.post(url, {
        "Details": stmt1.Details,
        "Posting_Date": stmt1.Posting_Date,
        "Description": "Updated description",
        "Amount": stmt1.Amount,
        "Type": stmt1.Type,
        "Balance": stmt1.Balance,
        "Acct_Info": stmt1.Acct_Info,
    })

    assert response.status_code in (200, 302)
    stmt1.refresh_from_db()
    assert stmt1.Description == "Updated description"

    # Denied update
    url = reverse("myfinances:transactions-update", args=[stmt2.pk])
    response = client.post(url, {
        "Details": stmt2.Details,
        "Posting_Date": stmt2.Posting_Date,
        "Description": "Hacked",
        "Amount": stmt2.Amount,
        "Type": stmt2.Type,
        "Balance": stmt2.Balance,
        "Acct_Info": stmt2.Acct_Info,
    })

    stmt2.refresh_from_db()
    assert stmt2.Description != "Hacked"


# ---------------------------------------------------------
# TransactionsDeleteView — group-restricted delete
# ---------------------------------------------------------

@pytest.mark.django_db
def test_transaction_delete_group_restricted(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    client.force_login(user)

    # Allowed delete
    url = reverse("myfinances:transactions-delete", args=[stmt1.pk])
    response = client.post(url)
    assert response.status_code in (200, 302)
    assert not Statements.objects.filter(pk=stmt1.pk).exists()

    # Denied delete
    url = reverse("myfinances:transactions-delete", args=[stmt2.pk])
    response = client.post(url)
    assert response.status_code == 404
    assert Statements.objects.filter(pk=stmt2.pk).exists()
