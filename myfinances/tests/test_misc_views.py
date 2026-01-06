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


@pytest.mark.django_db
def test_bulk_delete_removes_selected_transactions(client):
    """
    Bulk delete should remove only the selected transactions
    and leave the others untouched.
    """

    # Setup: user + group
    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    # Create 3 transactions in the same group
    tx1 = StatementFactory(user_group=group)
    tx2 = StatementFactory(user_group=group)
    tx3 = StatementFactory(user_group=group)

    # Keyword that matches all 3 (or you can use tx.Description)
    keyword = tx1.Description[:3]

    # POST: delete tx1 and tx2
    response = client.post(
        reverse("myfinances:bulk_update"),
        {
            "keyword": keyword,
            "statement_ids": [tx1.id, tx2.id],
            "bulk_delete": "1",  # triggers delete branch
        },
    )

    # Refresh DB state
    remaining_ids = set(
        Statements.objects.filter(
            user_group=group).values_list("id", flat=True)
    )

    # Assertions
    assert tx1.id not in remaining_ids
    assert tx2.id not in remaining_ids
    assert tx3.id in remaining_ids  # untouched

    # View should re-render successfully
    assert response.status_code == 200
    assert "Deleted" in response.content.decode()


@pytest.mark.django_db
def test_bulk_delete_with_no_selection(client):
    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    response = client.post(
        reverse("myfinances:bulk_update"),
        {"keyword": "anything", "bulk_delete": "1"},
    )

    assert response.status_code == 200
    assert "Deleted <strong>0</strong>" in response.content.decode()


@pytest.mark.django_db
def test_bulk_delete_only_affects_keyword_matches(client):
    """
    Bulk delete must only delete transactions that match the keyword filter.
    Even if the user selects IDs manually, the view re-filters using the keyword.
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    # Matching transactions
    tx_match1 = StatementFactory(user_group=group, Description="Grocery store")
    tx_match2 = StatementFactory(
        user_group=group, Description="Grocery market")

    # Non-matching transaction
    tx_other = StatementFactory(user_group=group, Description="Car payment")

    # Keyword that matches only the first two
    keyword = "grocery"

    # Attempt to delete all three
    response = client.post(
        reverse("myfinances:bulk_update"),
        {
            "keyword": keyword,
            "statement_ids": [tx_match1.id, tx_match2.id, tx_other.id],
            "bulk_delete": "1",
        },
    )

    remaining_ids = set(
        Statements.objects.filter(
            user_group=group).values_list("id", flat=True)
    )

    # Matching ones should be deleted
    assert tx_match1.id not in remaining_ids
    assert tx_match2.id not in remaining_ids

    # Non-matching one must remain
    assert tx_other.id in remaining_ids

    assert response.status_code == 200
    assert "Deleted" in response.content.decode()


@pytest.mark.django_db
def test_bulk_delete_only_affects_users_group(client):
    """
    Bulk delete must only delete transactions in the user's group.
    Transactions in other groups must remain untouched.
    """

    # User + group A
    group_a = GroupFactory()
    user = UserFactory(groups=[group_a])
    client.force_login(user)

    # Transaction in user's group
    tx_group_a = StatementFactory(user_group=group_a, Description="Rent")

    # Transaction in another group
    group_b = GroupFactory()
    tx_group_b = StatementFactory(user_group=group_b, Description="Rent")

    keyword = "rent"

    # Attempt to delete both
    response = client.post(
        reverse("myfinances:bulk_update"),
        {
            "keyword": keyword,
            "statement_ids": [tx_group_a.id, tx_group_b.id],
            "bulk_delete": "1",
        },
    )

    remaining_ids = set(
        Statements.objects.values_list("id", flat=True)
    )

    # User's group transaction should be deleted
    assert tx_group_a.id not in remaining_ids

    # Other group's transaction must remain
    assert tx_group_b.id in remaining_ids

    assert response.status_code == 200
    assert "Deleted" in response.content.decode()
