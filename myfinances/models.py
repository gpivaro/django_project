from django.db import models

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

