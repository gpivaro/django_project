import pytest
from django.urls import reverse

from myfinances.models import Statements
from myfinances.tests.factories import (
    UserFactory,
    GroupFactory,
    StatementFactory,
    CategoryFactory,
)


# =====================================================================
#  GET REQUEST TESTS
# =====================================================================

@pytest.mark.django_db
def test_bulk_update_get_no_keyword(client):
    """GET with no keyword returns empty queryset."""
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    StatementFactory(user_group=group, Description="Hello world")

    client.force_login(user)
    response = client.get(reverse("myfinances:bulk_update"))

    assert response.status_code == 200
    assert list(response.context["transactions"]) == []
    assert response.context["keyword"] == ""


@pytest.mark.django_db
def test_bulk_update_get_with_keyword(client):
    """GET with keyword returns filtered queryset."""
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    stmt1 = StatementFactory(user_group=group, Description="Grocery store")
    stmt2 = StatementFactory(user_group=group, Description="Electric bill")

    client.force_login(user)
    response = client.get(reverse("myfinances:bulk_update") + "?keyword=groc")

    txs = response.context["transactions"]
    assert stmt1 in txs
    assert stmt2 not in txs


@pytest.mark.django_db
def test_bulk_update_get_group_restricted(client):
    """GET must only return statements in the user's group."""
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1, Description="Match")
    stmt2 = StatementFactory(user_group=group2, Description="Match")

    client.force_login(user)
    response = client.get(reverse("myfinances:bulk_update") + "?keyword=Match")

    txs = response.context["transactions"]
    assert stmt1 in txs
    assert stmt2 not in txs


# =====================================================================
#  POST — BULK UPDATE TESTS
# =====================================================================

@pytest.mark.django_db
def test_bulk_update_group_restricted(client):
    """Bulk update must only update statements in the user's group."""
    group1 = GroupFactory()
    group2 = GroupFactory()

    user = UserFactory()
    user.groups.add(group1)

    stmt1 = StatementFactory(user_group=group1)
    stmt2 = StatementFactory(user_group=group2)

    cat = CategoryFactory(user_group=group1)

    client.force_login(user)
    url = reverse("myfinances:bulk_update")

    # Allowed update
    response = client.post(url, {
        "statement_ids": [stmt1.pk],
        "category_id": cat.pk
    })
    assert response.status_code in (200, 302)
    stmt1.refresh_from_db()
    assert stmt1.Category == cat

    # Denied update (cross-group)
    response = client.post(url, {
        "statement_ids": [stmt2.pk],
        "category_id": cat.pk
    })
    stmt2.refresh_from_db()
    assert stmt2.Category != cat


@pytest.mark.django_db
def test_bulk_update_post_bulk_update(client):
    """Bulk update should update all selected statements."""
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    old_cat = CategoryFactory(user_group=group)
    new_cat = CategoryFactory(user_group=group)

    stmt1 = StatementFactory(user_group=group, Category=old_cat)
    stmt2 = StatementFactory(user_group=group, Category=old_cat)

    client.force_login(user)

    response = client.post(
        reverse("myfinances:bulk_update"),
        {
            "keyword": "",
            "category_id": new_cat.id,
            "statement_ids": [stmt1.id, stmt2.id],
        },
    )

    stmt1.refresh_from_db()
    stmt2.refresh_from_db()

    assert stmt1.Category == new_cat
    assert stmt2.Category == new_cat
    assert response.context["updated_count"] == 2


# =====================================================================
#  POST — BULK DELETE TESTS
# =====================================================================

@pytest.mark.django_db
def test_bulk_delete_removes_selected_transactions(client):
    """Bulk delete removes only selected transactions."""
    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    tx1 = StatementFactory(user_group=group)
    tx2 = StatementFactory(user_group=group)
    tx3 = StatementFactory(user_group=group)

    keyword = tx1.Description[:3]

    response = client.post(
        reverse("myfinances:bulk_update"),
        {
            "keyword": keyword,
            "statement_ids": [tx1.id, tx2.id],
            "bulk_delete": "1",
        },
    )

    remaining_ids = set(
        Statements.objects.filter(
            user_group=group).values_list("id", flat=True)
    )

    assert tx1.id not in remaining_ids
    assert tx2.id not in remaining_ids
    assert tx3.id in remaining_ids
    assert response.status_code == 200
    assert "Deleted" in response.content.decode()


@pytest.mark.django_db
def test_bulk_delete_with_no_selection(client):
    """Bulk delete with no IDs selected should delete 0."""
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
    """Bulk delete must only delete keyword-matching statements."""
    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    tx_match1 = StatementFactory(user_group=group, Description="Grocery store")
    tx_match2 = StatementFactory(
        user_group=group, Description="Grocery market")
    tx_other = StatementFactory(user_group=group, Description="Car payment")

    keyword = "grocery"

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

    assert tx_match1.id not in remaining_ids
    assert tx_match2.id not in remaining_ids
    assert tx_other.id in remaining_ids
    assert response.status_code == 200
    assert "Deleted" in response.content.decode()


@pytest.mark.django_db
def test_bulk_delete_only_affects_users_group(client):
    """Bulk delete must not delete statements from other groups."""
    group_a = GroupFactory()
    user = UserFactory(groups=[group_a])
    client.force_login(user)

    tx_group_a = StatementFactory(user_group=group_a, Description="Rent")
    group_b = GroupFactory()
    tx_group_b = StatementFactory(user_group=group_b, Description="Rent")

    keyword = "rent"

    response = client.post(
        reverse("myfinances:bulk_update"),
        {
            "keyword": keyword,
            "statement_ids": [tx_group_a.id, tx_group_b.id],
            "bulk_delete": "1",
        },
    )

    remaining_ids = set(Statements.objects.values_list("id", flat=True))

    assert tx_group_a.id not in remaining_ids
    assert tx_group_b.id in remaining_ids
    assert response.status_code == 200
    assert "Deleted" in response.content.decode()


# =====================================================================
#  N+1 REGRESSION TEST
# =====================================================================

@pytest.mark.django_db
def test_bulk_update_no_n_plus_one(client, django_assert_num_queries):
    """Ensure GET does not perform N+1 queries."""
    group = GroupFactory()
    user = UserFactory()
    user.groups.add(group)

    for i in range(10):
        cat = CategoryFactory(user_group=group)
        StatementFactory(user_group=group, Category=cat, Description="Match")

    client.force_login(user)

    with django_assert_num_queries(4):
        response = client.get(
            reverse("myfinances:bulk_update") + "?keyword=Match")

    assert response.status_code == 200
