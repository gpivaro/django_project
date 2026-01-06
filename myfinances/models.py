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
    - An Owner (the individual user who uploaded the record).
    - A User Group (shared access: multiple users in the same group can view/update).
    - An optional Category (classification of the transaction).

    A database‑level UNIQUE CONSTRAINT is added to ensure that no two
    transactions in the same group can have the same identity. This prevents
    duplicate uploads across users in the same group, even during race
    conditions or future refactors.
    """

    # -----------------------------
    # Core transaction fields
    # -----------------------------
    Details = models.CharField(max_length=50)
    Posting_Date = models.DateField()
    Description = models.CharField(max_length=500)
    Amount = models.FloatField()
    Type = models.CharField(max_length=150)
    Balance = models.FloatField(blank=True)
    Check_Slip = models.TextField(blank=True)

    # -----------------------------
    # Ownership & classification
    # -----------------------------
    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,   # Prevent deletion of user from deleting records
        null=False,
        blank=False
    )

    Category = models.ForeignKey(
        'CategoryList',
        on_delete=models.SET_NULL,  # Keep transaction even if category is deleted
        null=True,
        blank=True,
        default=None
    )

    # -----------------------------
    # Group‑scoped access control
    # -----------------------------
    user_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="user_group_statements",
        help_text="User group that owns this transaction; all users in the group share access."
    )

    # -----------------------------
    # Additional metadata
    # -----------------------------
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

        # --------------------------------------------------------------
        # ⭐ DATABASE‑LEVEL UNIQUE CONSTRAINT
        # --------------------------------------------------------------
        # This ensures that no two transactions in the same group can have
        # the same identity. It protects against:
        #   - Duplicate uploads by different users in the same group
        #   - Duplicate uploads by the same user
        #   - Race conditions during simultaneous uploads
        #   - Future refactors accidentally removing duplicate checks
        #
        # This is the strongest possible guarantee of data integrity.
        # --------------------------------------------------------------
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user_group",
                    "Posting_Date",
                    "Description",
                    "Amount",
                    "Balance",
                    "Acct_Info",
                    "Type",
                    "Details",
                ],
                name="unique_transaction_per_group"
            )
        ]


class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
