from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


class Users(models.Model):
    email = models.EmailField(max_length=254, primary_key=True)
    name = models.CharField(max_length=155, default="Anonymous")
    joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email} | {self.name} | {self.joined}"

    class Meta:
        ordering = ["email"]


class Categories(models.Model):
    Group = models.TextField()
    Expression = models.TextField()
    Class = models.CharField(max_length=254, default="Non-categorized")
    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,   # ✅ prevent cascade delete
        null=False,                 # must always be set
        blank=False                 # required in forms
    )
    Insert_Date = models.DateTimeField(default=timezone.now)
    Update_Date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.Group}"

    class Meta:
        ordering = ["Group"]


class CategoryList(models.Model):
    name = models.CharField(max_length=100)

    label = models.CharField(
        max_length=50,
        choices=[
            ("Income", "Income"),
            ("Expense", "Expense"),
            ("Asset", "Asset"),
            ("Liability", "Liability"),
            ("Equity", "Equity"),
            ("Other", "Other"),
        ],
        default="Other",
        help_text="Assign a label to classify this category (e.g., Income, Expense, Asset, Liability)."
    )

    # Track who created the category (audit trail)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="owned_categories"
    )

    # ✅ Tie each category to a specific group
    user_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    insert_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Category List"
        ordering = ["name"]
        # ✅ Ensure uniqueness per group, not globally
        constraints = [
            models.UniqueConstraint(
                fields=["user_group", "name"],
                name="unique_category_per_group"
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("myfinances:category-detail", kwargs={'pk': self.pk})


class Statements(models.Model):
    """
    Statements model

    Represents a financial transaction record. Each record belongs to:
    - An Owner (the individual user who created/owns the record).
    - A User Group (shared access: multiple users in the same group can view/update).
    - An optional Category (classification of the transaction).

    Fields:
    -------
    Details       : Short string with transaction details (e.g., merchant info).
    Posting_Date  : Date the transaction was posted by the bank.
    Description   : Longer text description of the transaction.
    Amount        : Transaction amount (positive or negative).
    Type          : Transaction type (e.g., debit, credit).
    Balance       : Running balance after the transaction (optional).
    Check_Slip    : Optional check/slip reference text.
    Owner         : ForeignKey to the user who owns the record.
    Category      : ForeignKey to CategoryList for classification.
    User_Group    : ForeignKey to Django's built-in Group model, enabling
                    shared access across multiple users in the same group.
    Acct_Info     : Account identifier (last 4 digits).
    Insert_Date   : Timestamp when the record was inserted.
    Update_Date   : Timestamp automatically updated on save.
    """

    Details = models.CharField(max_length=50)
    Posting_Date = models.DateField()
    Description = models.TextField()
    Amount = models.FloatField()
    Type = models.CharField(max_length=150)
    Balance = models.FloatField(blank=True)
    Check_Slip = models.TextField(blank=True)

    # Owner: required, prevents cascade delete (records remain if user is deleted)
    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    # Category: optional classification
    Category = models.ForeignKey(
        'CategoryList',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )

    # User_Group: shared access across multiple users
    user_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="user_group_statements",
        help_text="User group that owns this transaction; all users in the group share access."
    )

    Acct_Info = models.CharField(max_length=4)
    Insert_Date = models.DateTimeField(default=timezone.now)
    Update_Date = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Readable string representation for admin/debugging."""
        return f"{self.Posting_Date} | {self.Description} | {self.Amount}"

    def get_absolute_url(self):
        """Return canonical URL for detail view of this transaction."""
        return reverse("myfinances:transactions-detail", kwargs={'pk': self.pk})

    class Meta:
        ordering = ["-Posting_Date"]  # newest transactions first


class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
