from django.db import models

# Create your models here.

ADD_EXPENSE_CHOICES = [
    ("Expense","Expense"),
    ("Income","Income")
]

SELECT_CATEGORY_CHOICES = [
    ("Food","Food"),
    ("Travel","Travel"),
    ("Shopping","Shopping"),
    ("Necessities","Necessities"),
    ("Entertainment","Entertainment"),
    ("Other","Other")
]

PROFESSION_CHOICES =[
    ("Employee","Employee"),
    ("Business","Business"),
    ("Student","Student"),
    ("Other","Other")
]

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Addmoney_info(models.Model):
    user = models.ForeignKey(
        User,
        default=1,
        on_delete=models.CASCADE
    )

    add_money = models.CharField(
        max_length=10,
        choices=ADD_EXPENSE_CHOICES
    )

    quantity = models.BigIntegerField()
    Date = models.DateField(default=now)

    Category = models.CharField(
        max_length=20,
        choices=SELECT_CATEGORY_CHOICES,
        default="Food"
    )

    class Meta:
        db_table = "addmoney"


class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profession = models.CharField(max_length = 10, choices=PROFESSION_CHOICES)
    Savings = models.IntegerField(null=True, blank=True)
    income = models.BigIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_image', blank=True)
    def __str__(self):
        return self.user.username