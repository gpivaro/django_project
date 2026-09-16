# models.py

# Create your models here.
from django.db import models


class GustoPayroll(models.Model):

    staff_member = models.CharField(max_length=255, null=False, blank=False)
    employee_initials = models.CharField(max_length=8, null=True, blank=False)
    payroll_period = models.CharField(max_length=255, null=True, blank=True)

    department = models.CharField(max_length=255, null=True, blank=True)

    regular_hours = models.FloatField(null=True, blank=True)
    regular_amount = models.FloatField(null=True, blank=True)
    regular_rate = models.FloatField(null=True, blank=True)

    time_off_hours = models.FloatField(null=True, blank=True)
    time_off_amount = models.FloatField(null=True, blank=True)
    time_off_rate = models.FloatField(null=True, blank=True)

    additional_earnings = models.FloatField(null=True, blank=True)
    gross_earnings = models.FloatField(null=True, blank=True)

    employee_taxes = models.FloatField(null=True, blank=True)
    federal_income_tax_employee = models.FloatField(null=True, blank=True)
    social_security_employee = models.FloatField(null=True, blank=True)
    medicare_employee = models.FloatField(null=True, blank=True)
    additional_medicare_employee = models.FloatField(null=True, blank=True)

    employer_taxes = models.FloatField(null=True, blank=True)
    social_security_employer = models.FloatField(null=True, blank=True)
    medicare_employer = models.FloatField(null=True, blank=True)
    tx_suta_employer = models.FloatField(null=True, blank=True)
    futa_employer = models.FloatField(null=True, blank=True)

    net_pay = models.FloatField(null=True, blank=True)
    reimbursements = models.FloatField(null=True, blank=True)
    donations = models.FloatField(null=True, blank=True)
    check_amount = models.FloatField(null=True, blank=True)

    employer_cost = models.FloatField(null=True, blank=True)

    employee_type = models.CharField(max_length=255, null=True, blank=True)
    payment = models.CharField(max_length=255, null=True, blank=True)

    payroll_period_start = models.DateField(null=True, blank=True)
    payroll_period_end = models.DateField(null=True, blank=True)

    hash_key = models.CharField(max_length=64, unique=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff_member} ({self.payroll_period_start} → {self.payroll_period_end})"
