import pytest
from django.urls import reverse
from myfinances.models import Statements
from myfinances.tests.factories import (
    GroupFactory,
    UserFactory,
    StatementFactory,
)


# =====================================================================
# 1. Landing page loads normally when no account is selected
# =====================================================================
@pytest.mark.django_db
def test_landing_page_no_acct_selected(client):
    """
    PURPOSE:
        Ensures the landing page renders correctly when the user has not
        selected any specific account (Acct_Info). This is the default
        behavior and must continue to work after introducing account filtering.

    WHAT IT TESTS:
        - Page loads successfully (HTTP 200)
        - Account selector renders all available accounts
        - Metrics section still appears
        - No filtering is applied
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    # Create transactions across multiple accounts
    StatementFactory(user_group=group, Acct_Info="1111")
    StatementFactory(user_group=group, Acct_Info="2222")

    response = client.get(reverse("myfinances:landing"))
    html = response.content.decode()

    assert response.status_code == 200
    assert "All Accounts" in html
    assert "1111" in html
    assert "2222" in html
    assert "Total Transactions" in html


# =====================================================================
# 2. Selecting an account filters the landing page metrics
# =====================================================================
@pytest.mark.django_db
def test_landing_page_filters_by_selected_acct(client):
    """
    PURPOSE:
        Verifies that selecting a specific account (?acct=XXXX) correctly
        filters the landing page metrics so that only transactions belonging
        to that account are counted.

    WHAT IT TESTS:
        - Only transactions for the selected Acct_Info are included
        - The selected account button is highlighted (Bootstrap 'active')
        - Metrics reflect filtered data
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    # Account 1111 (2 transactions)
    StatementFactory(user_group=group, Acct_Info="1111")
    StatementFactory(user_group=group, Acct_Info="1111")

    # Account 2222 (1 transaction)
    StatementFactory(user_group=group, Acct_Info="2222")

    response = client.get(reverse("myfinances:landing") + "?acct=1111")
    html = response.content.decode()

    # Should show only 2 transactions (acct 1111)
    assert response.context["total_transactions"] == 2

    # UI should highlight the selected account
    assert "1111" in html
    assert "active" in html


# =====================================================================
# 3. Selecting an account excludes transactions from other accounts
# =====================================================================
@pytest.mark.django_db
def test_landing_page_excludes_other_accounts(client):
    """
    PURPOSE:
        Ensures strict filtering: when an account is selected, transactions
        from other accounts must NOT appear in the metrics.

    WHAT IT TESTS:
        - Only the selected account's transactions are counted
        - Other accounts are excluded entirely
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    # Two accounts
    tx1 = StatementFactory(user_group=group, Acct_Info="1111")
    tx2 = StatementFactory(user_group=group, Acct_Info="2222")

    response = client.get(reverse("myfinances:landing") + "?acct=1111")

    assert response.context["total_transactions"] == 1
    assert tx1.Acct_Info == "1111"


# =====================================================================
# 4. Landing page only shows accounts belonging to the user's group
# =====================================================================
@pytest.mark.django_db
def test_landing_page_shows_only_group_accounts(client):
    """
    PURPOSE:
        Protects group-scoped security. A user must never see account
        identifiers (Acct_Info) belonging to another group.

    WHAT IT TESTS:
        - Account selector lists only accounts from the user's group
        - Accounts from other groups are not shown
    """

    group_a = GroupFactory()
    group_b = GroupFactory()

    user = UserFactory(groups=[group_a])
    client.force_login(user)

    # User's group
    StatementFactory(user_group=group_a, Acct_Info="1111")

    # Other group
    StatementFactory(user_group=group_b, Acct_Info="9999")

    response = client.get(reverse("myfinances:landing"))
    html = response.content.decode()

    assert "1111" in html
    assert "9999" not in html


# =====================================================================
# 5. Landing page metrics update correctly per account
# =====================================================================
@pytest.mark.django_db
def test_landing_page_metrics_are_account_specific(client):
    """
    PURPOSE:
        Ensures that ALL landing page metrics (total transactions, grand total,
        uncategorized count, category count) are recalculated based on the
        selected account.

    WHAT IT TESTS:
        - Grand total reflects only the selected account
        - Transaction count reflects only the selected account
        - Filtering logic is applied BEFORE metrics are computed
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])
    client.force_login(user)

    # Account 1111
    StatementFactory(user_group=group, Acct_Info="1111", Amount=50)
    StatementFactory(user_group=group, Acct_Info="1111", Amount=100)

    # Account 2222
    StatementFactory(user_group=group, Acct_Info="2222", Amount=999)

    response = client.get(reverse("myfinances:landing") + "?acct=1111")

    assert response.context["grand_total"] == 150
    assert response.context["total_transactions"] == 2
