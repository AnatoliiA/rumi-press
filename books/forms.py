from django import forms
from .models import Book


class BookForm(forms.ModelForm):

    class Meta:
        model = Book

        fields = [
            "title",
            "subtitle",
            "authors",
            "publisher",
            "published_date",
            "category",
            "distribution_expense",
            "quantity",
        ]

        widgets = {
            "published_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }