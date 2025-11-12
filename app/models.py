from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
# Create your models here.
class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_price_id = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    features = models.TextField(help_text="Comma-separated list of features")

    start_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(null=True, blank=True)

    def get_feature_list(self):
        return self.features.split(",")

    def __str__(self):
        return f"{self.user.username} - {self.display_name}"


class Prompt(models.Model):
    content = models.TextField()

    def __str__(self):
        return f"{self.content[:50]}..."