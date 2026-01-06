import io
import pytest
from django.urls import reverse
from myfinances.models import Statements
from myfinances.tests.factories import UserFactory, GroupFactory


@pytest.mark.django_db
def test_banktransactions_group_duplicate_rejection(client):
    """
    If User A uploads a transaction, User B in the same group must not be able
    to upload the same transaction again.
    """

    group = GroupFactory()
    user_a = UserFactory(groups=[group])
    user_b = UserFactory(groups=[group])

    csv_content = (
        "Header Row To Skip\n"
        "Details,2025-01-01,Test Description,10.00,DEBIT,100.00,,\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))
    csv_file.name = "test.csv"

    # First upload
    client.force_login(user_a)
    client.post(
        reverse("myfinances:banktransactions"),
        {"file": csv_file, "acct_last4": "1234"},
        format="multipart"
    )
    assert Statements.objects.count() == 1

    # Reset file pointer
    csv_file.seek(0)

    # Second upload by another user in same group
    client.force_login(user_b)
    client.post(
        reverse("myfinances:banktransactions"),
        {"file": csv_file, "acct_last4": "1234"},
        format="multipart"
    )

    assert Statements.objects.count() == 1


@pytest.mark.django_db
def test_banktransactions_same_user_duplicate_rejection(client):
    """
    Uploading the same CSV twice by the same user must not create duplicates.
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])

    csv_content = (
        "Header Row To Skip\n"
        "Details,2025-01-01,Test Description,10.00,DEBIT,100.00,,\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))
    csv_file.name = "test.csv"

    client.force_login(user)

    # First upload
    client.post(
        reverse("myfinances:banktransactions"),
        {"file": csv_file, "acct_last4": "9999"},
        format="multipart"
    )
    assert Statements.objects.count() == 1

    # Reset pointer
    csv_file.seek(0)

    # Second upload
    client.post(
        reverse("myfinances:banktransactions"),
        {"file": csv_file, "acct_last4": "9999"},
        format="multipart"
    )

    assert Statements.objects.count() == 1


@pytest.mark.django_db
def test_banktransactions_accepts_multiple_unique_rows(client):
    """
    A CSV containing multiple different transactions must save all of them.
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])

    csv_content = (
        "Header Row To Skip\n"
        "Details,2025-01-01,Desc1,10.00,DEBIT,100.00,,\n"
        "Details,2025-01-02,Desc2,20.00,DEBIT,120.00,,\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))
    csv_file.name = "multi.csv"

    client.force_login(user)

    client.post(
        reverse("myfinances:banktransactions"),
        {"file": csv_file, "acct_last4": "1111"},
        format="multipart"
    )

    assert Statements.objects.count() == 2


@pytest.mark.django_db
def test_banktransactions_invalid_rows_declined(client):
    """
    Rows with invalid numeric or date fields must be skipped.
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])

    csv_content = (
        "Header Row To Skip\n"
        "Details,INVALID_DATE,Desc1,10.00,DEBIT,100.00,,\n"
        "Details,2025-01-01,Desc2,INVALID_AMOUNT,DEBIT,100.00,,\n"
        "Details,2025-01-01,Desc3,10.00,DEBIT,INVALID_BALANCE,,\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))
    csv_file.name = "invalid.csv"

    client.force_login(user)

    client.post(
        reverse("myfinances:banktransactions"),
        {"file": csv_file, "acct_last4": "2222"},
        format="multipart"
    )

    # All rows invalid → nothing saved
    assert Statements.objects.count() == 0


@pytest.mark.django_db
def test_banktransactions_acct_last4_applied(client):
    """
    Uploaded transactions must store the acct_last4 value.
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])

    csv_content = (
        "Header Row To Skip\n"
        "Details,2025-01-01,Desc,10.00,DEBIT,100.00,,\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))
    csv_file.name = "acct.csv"

    client.force_login(user)

    client.post(
        reverse("myfinances:banktransactions"),
        {"file": csv_file, "acct_last4": "5555"},
        format="multipart"
    )

    stmt = Statements.objects.first()
    assert stmt.Acct_Info == "5555"


@pytest.mark.django_db
def test_banktransactions_fields_saved_correctly(client):
    """
    Ensure all parsed fields (Details, Type, Description, etc.) are saved.
    """

    group = GroupFactory()
    user = UserFactory(groups=[group])

    csv_content = (
        "Header Row To Skip\n"
        "DETAILS,2025-01-01,My Desc,15.50,CREDIT,200.00,CHK123,\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))
    csv_file.name = "fields.csv"

    client.force_login(user)

    client.post(
        reverse("myfinances:banktransactions"),
        {"file": csv_file, "acct_last4": "7777"},
        format="multipart"
    )

    stmt = Statements.objects.first()

    assert stmt.Details == "DETAILS"
    assert stmt.Description == "My Desc"
    assert stmt.Type == "CREDIT"
    assert stmt.Amount == 15.50
    assert stmt.Balance == 200.00
    assert stmt.Check_Slip == "CHK123"
    assert stmt.Acct_Info == "7777"
