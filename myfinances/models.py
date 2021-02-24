from django.db import models
from django.utils import timezone

# Create your models here.
class Statement(models.Model):
    Details = models.CharField(max_length=50)
    Posting_Date = models.DateTimeField(auto_now_add=False)
    Description = models.TextField()
    Amount = models.FloatField()
    Type = models.CharField(max_length=150)
    Balance = models.FloatField(blank=True)
    Check_Slip = models.IntegerField(blank=True)

    def __str__(self):
        return f"{self.Posting_Date} | {self.Description} | {self.Amount}"

    class Meta:
        ordering = ["-Posting_Date"]


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
    Owner = models.ForeignKey(Users, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.Group} | {self.Expression}"

    class Meta:
        ordering = ["Group"]

