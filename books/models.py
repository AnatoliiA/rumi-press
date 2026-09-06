from django.conf import settings
from django.db import models


class Title(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be blank.")
        return super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Book(Title):
    subtitle = models.CharField(max_length=255, blank=True)

    authors = models.TextField()
    publisher = models.CharField(max_length=255)

    published_date = models.DateField(
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="books"
    )

    distribution_expense = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    def getSubtitle(self):
        return (
            f"{self.subtitle} by {self.authors} "
            f"published by {self.publisher} "
            f"on {self.published_date} "
            f"in category {self.category} "
            f"with distribution expense of {self.distribution_expense} "
            f"and quantity of {self.quantity}"
        )

    def __str__(self):
        return self.title

class BookHistory(models.Model):

    ACTION_CHOICES = [
        ("ADD", "Added"),
        ("REMOVE", "Removed"),
        ("DELETE", "Deleted"),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history"
    )

    book_title = models.CharField(
        max_length=255
    )

    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES
    )

    quantity = models.PositiveIntegerField(
        default=0
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def get(self):
        return f"{self.book_title} - {self.quantity} - {self.action} - {self.user} - {self.created_at}"

    def __str__(self):
        return f"{self.book_title} - {self.action}"