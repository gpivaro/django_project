from django.db import models
from django.utils import timezone
from django.conf import settings



class Users(models.Model):
    email = models.EmailField(max_length=254, primary_key=True)
    name = models.CharField(max_length=155, default="Anonymous")
    joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email} | {self.name} | {self.joined}"

    class Meta:
        ordering = ["email"]
        


from django.conf import settings
from django.utils import timezone
from django.db import models

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



class Statements(models.Model):
    Details = models.CharField(max_length=50)
    Posting_Date = models.DateField()
    Description = models.TextField()
    Amount = models.FloatField()
    Type = models.CharField(max_length=150)
    Balance = models.FloatField(blank=True)
    Check_Slip = models.TextField(blank=True)
    Owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,   # prevents cascade delete
        null=False,                 # must always be set
        blank=False                 # required in forms
    )
    Category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )
    Insert_Date = models.DateTimeField(default=timezone.now)
    Update_Date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.Posting_Date} | {self.Description} | {self.Amount}"

    class Meta:
        ordering = ["-Posting_Date"]


class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
