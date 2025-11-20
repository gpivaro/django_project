from django.db import models
from django.utils import timezone




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
    Insert_Date = models.DateTimeField(default=timezone.now)
    Update_Date = models.DateTimeField(auto_now=True)         # updates on every save


    def __str__(self):
        # return f"{self.Group} | {self.Expression}"
        return f"{self.Group} | {self.Expression}"

    class Meta:
        ordering = ["Group"]

# Create your models here.
class Statements(models.Model):
    Details = models.CharField(max_length=50)
    Posting_Date = models.DateTimeField(auto_now_add=False)
    Description = models.TextField()
    Amount = models.FloatField()
    Type = models.CharField(max_length=150)
    Balance = models.FloatField(blank=True)
    Check_Slip = models.TextField(blank=True)
    Owner = models.ForeignKey(Users, on_delete=models.CASCADE, default='gfp.1@hotmail.com')
    Insert_Date = models.DateTimeField(default=timezone.now)
    Update_Date = models.DateTimeField(auto_now=True)         # updates on every save

    def __str__(self):
        return f"{self.Posting_Date} | {self.Description} | {self.Amount} "

    class Meta:
        ordering = ["-Posting_Date"]


class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
