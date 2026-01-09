import pytest
from django.urls import reverse
from myfinances.tests.factories import (
    UserFactory,
    GroupFactory,
    CategoryFactory,
    StatementFactory,
)


# =====================================================================
# FIXTURES
# =====================================================================

@pytest.fixture
def setup_user(db):
    """
    Create a user and a group for CSV export tests.
    """
    user = UserFactory()
    group = GroupFactory()
    user.groups.add(group)
    return user, group


@pytest.fixture
def categories(db, setup_user):
    """
    Create two categories for testing using factories.
    """
    user, group = setup_user

    income = CategoryFactory(
        name="Salary",
        label="Income",
        owner=user,
        user_group=group,
    )

    expense = CategoryFactory(
        name="Food",
        label="Expense",
        owner=user,
        user_group=group,
    )

    return income, expense


# =====================================================================
# ACCESS CONTROL TESTS
# =====================================================================

@pytest.mark.django_db
def test_balance_sheet_requires_login(client):
    """
    Anonymous users must be redirected to login.
    """
    url = reverse("myfinances:balance_sheet")
    response = client.get(url)

    assert response.status_code == 302
    assert "/login" in response.url.lower()


@pytest.mark.django_db
def test_balance_sheet_group_restricted(client):
    """
    Users must only see statements belonging to their own group.
    """
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


# =====================================================================
# CSV EXPORT TESTS
# =====================================================================

@pytest.mark.django_db
def test_balance_sheet_csv_export_basic(client, setup_user, categories):
    """
    CSV export should include only rows from the selected account.
    """
    user, group = setup_user
    income, expense = categories

    # Selected account
    StatementFactory(
        Owner=user,
        user_group=group,
        Acct_Info="Chec",
        Category=income,
        Amount=100,
        Posting_Date="2024-01-10"
    )
    StatementFactory(
        Owner=user,
        user_group=group,
        Acct_Info="Chec",
        Category=expense,
        Amount=-50,
        Posting_Date="2024-01-15"
    )

    # Other account (excluded)
    StatementFactory(
        Owner=user,
        user_group=group,
        Acct_Info="Savi",
        Category=income,
        Amount=999,
        Posting_Date="2024-01-20"
    )

    client.force_login(user)

    url = reverse("myfinances:balance_sheet")
    response = client.get(
        url,
        {
            "export": "csv",
            "acct_info": "Chec",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        },
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"

    content = response.content.decode()

    assert "Chec" in content
    assert "100" in content
    assert "-50" in content

    assert "Savi" not in content
    assert "999" not in content


@pytest.mark.django_db
def test_balance_sheet_csv_export_multi_account(client, setup_user, categories):
    """
    CSV export should include rows from multiple selected accounts.
    """
    user, group = setup_user
    income, expense = categories

    StatementFactory(
        Owner=user, user_group=group,
        Acct_Info="Chec", Category=income, Amount=100, Posting_Date="2024-01-10"
    )
    StatementFactory(
        Owner=user, user_group=group,
        Acct_Info="Savi", Category=expense, Amount=-25, Posting_Date="2024-01-15"
    )
    StatementFactory(
        Owner=user, user_group=group,
        Acct_Info="Cred", Category=income, Amount=777, Posting_Date="2024-01-15",
    )

    client.force_login(user)

    url = reverse("myfinances:balance_sheet")
    response = client.get(
        url,
        {
            "export": "csv",
            "acct_info": '["Chec","Savi"]',
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        },
    )

    content = response.content.decode()

    assert "Chec" in content
    assert "Savi" in content
    assert "100" in content
    assert "-25" in content

    assert "Cred" not in content
    assert "777" not in content


@pytest.mark.django_db
def test_balance_sheet_csv_export_category_filter(client, setup_user, categories):
    """
    CSV export should respect category filtering.
    """
    user, group = setup_user
    income, expense = categories

    StatementFactory(
        Owner=user, user_group=group,
        Acct_Info="Chec", Category=income, Amount=500, Posting_Date="2024-01-15"
    )
    StatementFactory(
        Owner=user, user_group=group,
        Acct_Info="Chec", Category=expense, Amount=-40, Posting_Date="2024-01-15"
    )

    client.force_login(user)

    url = reverse("myfinances:balance_sheet")
    response = client.get(
        url,
        {
            "export": "csv",
            "acct_info": "Chec",
            "category": "Salary",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        },
    )

    content = response.content.decode()

    assert "500" in content
    assert "Salary" in content

    assert "-40" not in content
    assert "Food" not in content


@pytest.mark.django_db
def test_balance_sheet_csv_export_does_not_break_page(client, setup_user, categories):
    """
    Exporting CSV must not break the page or corrupt the response pipeline.
    """
    user, group = setup_user
    income, _ = categories

    for _ in range(500):
        StatementFactory(
            Owner=user,
            user_group=group,
            Acct_Info="Chec",
            Category=income,
            Amount=10,
            Posting_Date="2024-01-15"
        )

    client.force_login(user)

    url = reverse("myfinances:balance_sheet")

    response = client.get(
        url,
        {
            "export": "csv",
            "acct_info": "Chec",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        },
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"

    page_response = client.get(url)
    assert page_response.status_code == 200
    assert b"Balance Sheet" in page_response.content
