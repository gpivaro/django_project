import pytest
from django.urls import reverse
from datetime import date, timedelta

from myfinances.tests.factories import (
    UserFactory,
    GroupFactory,
    StatementFactory,
    CategoryFactory,
)


# =====================================================================
#  GROUP SCOPING
# =====================================================================

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


# =====================================================================
#  ACCOUNT FILTERING (single account only)
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_filters_by_single_account(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    stmt1 = StatementFactory(user_group=group, Acct_Info="CHK1")
    stmt2 = StatementFactory(user_group=group, Acct_Info="SAV1")

    client.force_login(user)
    url = reverse("myfinances:transactions-list")

    response = client.get(f"{url}?acct_info=CHK1")
    txs = response.context["transactions"]

    assert stmt1 in txs
    assert stmt2 not in txs


@pytest.mark.django_db
def test_transactions_list_account_context(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    StatementFactory(user_group=group, Acct_Info="CHK1")
    StatementFactory(user_group=group, Acct_Info="SAV1")

    client.force_login(user)
    response = client.get(reverse("myfinances:transactions-list"))

    assert set(response.context["available_accounts"]) == {"CHK1", "SAV1"}
    assert response.context["selected_accounts"] == []


@pytest.mark.django_db
def test_transactions_list_selected_accounts_in_context(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    StatementFactory(user_group=group, Acct_Info="CHK1")

    client.force_login(user)
    url = reverse("myfinances:transactions-list")

    response = client.get(f"{url}?acct_info=CHK1")

    assert response.context["selected_accounts"] == ["CHK1"]


@pytest.mark.django_db
def test_transactions_list_account_filter_group_scoped(client):
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1, Acct_Info="CHK1")
    stmt2 = StatementFactory(user_group=group2, Acct_Info="CHK1")

    client.force_login(user)
    url = reverse("myfinances:transactions-list")

    response = client.get(f"{url}?acct_info=CHK1")
    txs = response.context["transactions"]

    assert stmt1 in txs
    assert stmt2 not in txs


# =====================================================================
#  N+1 REGRESSION (updated expected query count)
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_no_n_plus_one(client, django_assert_num_queries):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    for i in range(10):
        cat = CategoryFactory(name=f"Cat{i}")
        StatementFactory(Category=cat, user_group=group, Acct_Info="CHK1")

    client.force_login(user)

    # Expected:
    # 1 session
    # 1 user
    # 1 count() for pagination
    # 1 aggregate() for total
    # 1 count() for record_count
    # 1 distinct acct_info
    # 1 main queryset
    # 1 category list
    with django_assert_num_queries(8):
        response = client.get(reverse("myfinances:transactions-list"))
        assert response.status_code == 200


# =====================================================================
#  PAGINATION
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_default_pagination(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    StatementFactory.create_batch(30, user_group=group)

    client.force_login(user)

    response = client.get(reverse("myfinances:transactions-list"))
    assert response.context["is_paginated"] is True
    assert len(response.context["transactions"]) == 20


@pytest.mark.django_db
def test_transactions_list_custom_page_size(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    StatementFactory.create_batch(50, user_group=group)

    client.force_login(user)

    response = client.get(
        reverse("myfinances:transactions-list") + "?page_size=10"
    )
    assert len(response.context["transactions"]) == 10


@pytest.mark.django_db
def test_transactions_list_page_size_all(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    StatementFactory.create_batch(50, user_group=group)

    client.force_login(user)

    response = client.get(
        reverse("myfinances:transactions-list") + "?page_size=all"
    )
    assert response.context["is_paginated"] is False
    assert len(response.context["transactions"]) == 50


# =====================================================================
#  DESCRIPTION FILTER
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_description_filter(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    stmt1 = StatementFactory(user_group=group, Description="Grocery store")
    stmt2 = StatementFactory(user_group=group, Description="Electric bill")

    client.force_login(user)

    response = client.get(
        reverse("myfinances:transactions-list") + "?description=groc"
    )
    txs = response.context["transactions"]

    assert stmt1 in txs
    assert stmt2 not in txs


# =====================================================================
#  CATEGORY FILTER
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_category_filter(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    cat_food = CategoryFactory(name="Food")
    cat_util = CategoryFactory(name="Utilities")

    stmt1 = StatementFactory(user_group=group, Category=cat_food)
    stmt2 = StatementFactory(user_group=group, Category=cat_util)

    client.force_login(user)

    response = client.get(
        reverse("myfinances:transactions-list") + "?category=Food"
    )
    txs = response.context["transactions"]

    assert stmt1 in txs
    assert stmt2 not in txs


# =====================================================================
#  DATE RANGE FILTER
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_date_range_filter(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    today = date.today()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    stmt1 = StatementFactory(user_group=group, Posting_Date=today)
    stmt2 = StatementFactory(user_group=group, Posting_Date=last_week)

    client.force_login(user)

    url = reverse("myfinances:transactions-list")
    response = client.get(f"{url}?start_date={yesterday}&end_date={today}")

    txs = response.context["transactions"]

    assert stmt1 in txs
    assert stmt2 not in txs


# =====================================================================
#  TOTAL AMOUNT
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_total_amount(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    stmt1 = StatementFactory(user_group=group, Amount=100)
    stmt2 = StatementFactory(user_group=group, Amount=50)

    client.force_login(user)

    response = client.get(reverse("myfinances:transactions-list"))
    assert response.context["total_amount"] == 150


# =====================================================================
#  CSV EXPORT
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_csv_export(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    stmt = StatementFactory(user_group=group, Amount=123.45)

    client.force_login(user)

    url = reverse("myfinances:transactions-list") + "?export=csv"
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"

    content = response.content.decode()

    assert "Transactions Export" in content
    assert "123.45" in content
    assert stmt.Description in content


# =====================================================================
#  COMBINED FILTERS
# =====================================================================

@pytest.mark.django_db
def test_transactions_list_combined_filters(client):
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    cat = CategoryFactory(name="Food")

    stmt1 = StatementFactory(
        user_group=group,
        Description="Lunch",
        Category=cat,
        Posting_Date=date.today(),
    )

    stmt2 = StatementFactory(
        user_group=group,
        Description="Dinner",
        Category=cat,
        Posting_Date=date.today() - timedelta(days=10),
    )

    client.force_login(user)

    url = reverse("myfinances:transactions-list")
    response = client.get(
        f"{url}?description=lun&category=Food&start_date={date.today()}&end_date={date.today()}"
    )

    txs = response.context["transactions"]

    assert stmt1 in txs
    assert stmt2 not in txs
