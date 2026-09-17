# models.py

from django.db import models


class GustoPayroll(models.Model):
    """
    Represents a single payroll record imported from a Gusto payroll CSV.

    Each row corresponds to one employee for one payroll period.
    Deduplication is enforced using the `hash_key` field, which is unique.

    Fields include:
    - Staff identity (short name + initials)
    - Payroll period (raw string + start/end dates)
    - Department and employee type
    - All regular, time-off, and additional earnings
    - All employee and employer tax components
    - Net pay, reimbursements, donations, check amount
    - Employer cost
    - Hash key for deduplication
    - Insert timestamp
    """

    # ---------------------------------------------------------
    # Identity fields
    # ---------------------------------------------------------
    staff_member = models.CharField(max_length=255, null=False, blank=False)
    employee_initials = models.CharField(max_length=8, null=True, blank=False)

    # Raw payroll period string (e.g., "2025-06-08 - 2025-06-21")
    payroll_period = models.CharField(max_length=255, null=True, blank=True)

    # Department (e.g., "Massage", "SLP", "Admin")
    department = models.CharField(max_length=255, null=True, blank=True)

    # ---------------------------------------------------------
    # Regular earnings
    # ---------------------------------------------------------
    regular_hours = models.FloatField(null=True, blank=True)
    regular_amount = models.FloatField(null=True, blank=True)
    regular_rate = models.FloatField(null=True, blank=True)

    # ---------------------------------------------------------
    # Time-off earnings
    # ---------------------------------------------------------
    time_off_hours = models.FloatField(null=True, blank=True)
    time_off_amount = models.FloatField(null=True, blank=True)
    time_off_rate = models.FloatField(null=True, blank=True)

    # ---------------------------------------------------------
    # Additional earnings
    # ---------------------------------------------------------
    additional_earnings = models.FloatField(null=True, blank=True)
    gross_earnings = models.FloatField(null=True, blank=True)

    # ---------------------------------------------------------
    # Employee taxes
    # ---------------------------------------------------------
    employee_taxes = models.FloatField(null=True, blank=True)
    federal_income_tax_employee = models.FloatField(null=True, blank=True)
    social_security_employee = models.FloatField(null=True, blank=True)
    medicare_employee = models.FloatField(null=True, blank=True)
    additional_medicare_employee = models.FloatField(null=True, blank=True)

    # ---------------------------------------------------------
    # Employer taxes
    # ---------------------------------------------------------
    employer_taxes = models.FloatField(null=True, blank=True)
    social_security_employer = models.FloatField(null=True, blank=True)
    medicare_employer = models.FloatField(null=True, blank=True)
    tx_suta_employer = models.FloatField(null=True, blank=True)
    futa_employer = models.FloatField(null=True, blank=True)

    # ---------------------------------------------------------
    # Net pay and other payments
    # ---------------------------------------------------------
    net_pay = models.FloatField(null=True, blank=True)
    reimbursements = models.FloatField(null=True, blank=True)
    donations = models.FloatField(null=True, blank=True)
    check_amount = models.FloatField(null=True, blank=True)

    # Total employer cost for this employee in this period
    employer_cost = models.FloatField(null=True, blank=True)

    # ---------------------------------------------------------
    # Employee metadata
    # ---------------------------------------------------------
    employee_type = models.CharField(max_length=255, null=True, blank=True)
    payment = models.CharField(max_length=255, null=True, blank=True)

    # ---------------------------------------------------------
    # Payroll period dates (converted from raw string)
    # ---------------------------------------------------------
    payroll_period_start = models.DateField(null=True, blank=True)
    payroll_period_end = models.DateField(null=True, blank=True)

    # ---------------------------------------------------------
    # Deduplication + audit fields
    # ---------------------------------------------------------
    hash_key = models.CharField(max_length=64, unique=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Human-readable representation of the payroll row.
        Example:
            "Angela P (2025-06-08 → 2025-06-21)"
        """
        return f"{self.staff_member} ({self.payroll_period_start} → {self.payroll_period_end})"


# models.py (add this below GustoPayroll)

class XeroTransaction(models.Model):
    """
    Represents a single financial transaction imported from Xero.

    Each row corresponds to one ledger entry.
    Deduplication is enforced using the `hash_key` field.
    """

    # Core transaction fields
    date = models.DateField(null=True, blank=True)
    account_type = models.CharField(max_length=255, null=True, blank=True)
    related_account = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # Monetary fields
    debit = models.FloatField(null=True, blank=True)
    credit = models.FloatField(null=True, blank=True)
    gross = models.FloatField(null=True, blank=True)

    category = models.CharField(max_length=255, null=True, blank=True)

    # Deduplication + audit
    hash_key = models.CharField(max_length=64, unique=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} — {self.contact} — {self.description}"


class JaneSessions(models.Model):
    """
    Represents a single billing item from Jane's 'Sessions by Staff Member' export.
    Each row corresponds to one billed service.
    """

    staff_member = models.CharField(max_length=255, null=True, blank=True)
    employee_initials = models.CharField(max_length=50, null=True, blank=True)

    purchase_date = models.DateField(null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    item = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    subtotal = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    collected = models.FloatField(null=True, blank=True)
    balance = models.FloatField(null=True, blank=True)

    # Deduplication + audit
    hash_key = models.CharField(max_length=64, unique=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.purchase_date} — {self.staff_member} — {self.item}"


class JaneProcessedClaim(models.Model):
    """
    Represents a single payment/claim from Jane's Payments export.
    """

    payment_date = models.DateField(null=True, blank=True)
    payer = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=255, null=True, blank=True)
    reference_number = models.CharField(max_length=255, null=True, blank=True)
    applied_to = models.TextField(null=True, blank=True)
    claim_count = models.FloatField(null=True, blank=True)

    amount = models.FloatField(null=True, blank=True)
    processing_fee = models.FloatField(null=True, blank=True)
    amount_paid_to_clinic = models.FloatField(null=True, blank=True)

    # Deduplication + audit
    hash_key = models.CharField(max_length=64, unique=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_date} — {self.payer} — {self.amount}"
