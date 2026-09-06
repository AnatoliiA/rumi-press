from datetime import timedelta

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
import logging
from .models import Book, BookHistory
from .forms import BookForm

logger = logging.getLogger(__name__)


# =========================================================
# BOOK LIST
# =========================================================

@login_required
def book_list(request):
    logger.debug("Fetching book list for user: %s", request.user)
    logger.info("User %s accessed the book list.", request.user)
    books = (
        Book.objects
        .select_related("category")
        .order_by("title")
    )

    return render(
        request,
        "books/book_list.html",
        {
            "books": books
        }
    )


# =========================================================
# ADD BOOK
# =========================================================

@login_required
def book_add(request):
    logger.debug("User %s is attempting to add a new book.", request.user)
    logger.info("User %s accessed the add book page.", request.user)
    logger.debug("Request method: %s", request.method)
    if request.method == "POST":

        form = BookForm(request.POST)

        if form.is_valid():

            book = form.save()
            logger.debug("Book created: %s", book.getSubtitle())
            
            bh = BookHistory.objects.create(
                book=book,
                book_title=book.title,
                action="ADD",
                quantity=book.quantity,
                user=request.user
            )

            messages.success(
                request,
                f"{book.quantity} copies of '{book.title}' added."
            )

            logger.debug("BookHistory entry created: %s", bh.get())
            logger.info("Book added by user: %s", request.user)

            return redirect(
                "books:book_list"
            )

    else:

        form = BookForm()
        logger.debug("form %s", form)

    return render(
        request,
        "books/book_form.html",
        {
            "form": form,
            "title": "Add Book"
        }
    )


# =========================================================
# BOOK DETAIL
# =========================================================

@login_required
def book_detail(request, pk):

    book = get_object_or_404(
        Book.objects.select_related("category"),
        pk=pk
    )

    return render(
        request,
        "books/book_detail.html",
        {
            "book": book
        }
    )


# =========================================================
# EDIT BOOK
# =========================================================

@login_required
def book_edit(request, pk):

    book = get_object_or_404(
        Book,
        pk=pk
    )

    if request.method == "POST":

        form = BookForm(
            request.POST,
            instance=book
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Book updated successfully."
            )

            return redirect(
                "books:book_list"
            )

    else:

        form = BookForm(
            instance=book
        )

    return render(
        request,
        "books/book_form.html",
        {
            "form": form,
            "title": "Edit Book"
        }
    )


# =========================================================
# REMOVE BOOK QUANTITY
# =========================================================

@login_required
def book_delete(request, pk):

    book = Book.objects.filter(
        pk=pk
    ).first()

    if book is None:

        messages.warning(
            request,
            "This book no longer exists."
        )

        return redirect(
            "books:book_list"
        )

    if request.method == "POST":

        try:

            remove_quantity = int(
                request.POST.get(
                    "quantity",
                    1
                )
            )

        except (ValueError, TypeError):

            remove_quantity = 0


        if remove_quantity <= 0:

            messages.error(
                request,
                "Quantity must be greater than 0."
            )

            return redirect(
                "books:book_delete",
                pk=book.pk
            )


        if remove_quantity > book.quantity:

            messages.error(
                request,
                "You cannot remove more books than are available."
            )

            return redirect(
                "books:book_delete",
                pk=book.pk
            )


        # Записываем операцию в историю

        BookHistory.objects.create(
            book=book,
            book_title=book.title,
            action="REMOVE",
            quantity=remove_quantity,
            user=request.user
        )


        # Уменьшаем количество

        book.quantity -= remove_quantity


        # Если осталось 0 экземпляров,
        # удаляем книгу полностью

        if book.quantity == 0:

            title = book.title

            book.delete()

            messages.success(
                request,
                f"All copies of '{title}' removed. Book deleted."
            )

        else:

            book.save(
                update_fields=["quantity"]
            )

            messages.success(
                request,
                f"{remove_quantity} copies removed. "
                f"{book.quantity} remaining."
            )


        return redirect(
            "books:book_list"
        )


    return render(
        request,
        "books/book_confirm_delete.html",
        {
            "book": book
        }
    )


# =========================================================
# HISTORY
# =========================================================

@login_required
def book_history(request):

    history = (
        BookHistory.objects
        .select_related("user")
        .order_by("-created_at")
    )

    return render(
        request,
        "books/book_history.html",
        {
            "history": history
        }
    )


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    # -----------------------------------------------------
    # PERIOD
    # -----------------------------------------------------

    try:
        period = int(request.GET.get("period",7))
    except (ValueError, TypeError):
        period = 7


    allowed_periods = [
        7, 30, 90, 365
    ]


    if period not in allowed_periods:
        period = 7
    # 
    today = timezone.localdate()

    start_date = (
        today
        - timedelta(
            days=period - 1
        )
    )


    # -----------------------------------------------------
    # HISTORY FOR SELECTED PERIOD
    # -----------------------------------------------------

    history = BookHistory.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=today
    )


    # -----------------------------------------------------
    # TOTAL INCOMING
    # -----------------------------------------------------

    incoming = (
        history
        .filter(
            action="ADD"
        )
        .aggregate(total=Sum("quantity"))["total"]
        or 0
    )


    # -----------------------------------------------------
    # TOTAL OUTGOING
    # -----------------------------------------------------

    outgoing = (
        history
        .filter(
            action__in=[
                "REMOVE",
                "DELETE"
            ]
        )
        .aggregate(
            total=Sum("quantity")
        )["total"]
        or 0
    )


    # -----------------------------------------------------
    # CURRENT NUMBER OF BOOK COPIES
    # -----------------------------------------------------

    total_books = (
        Book.objects
        .aggregate(
            total=Sum("quantity")
        )["total"]
        or 0
    )


    # -----------------------------------------------------
    # NUMBER OF DIFFERENT BOOK TITLES
    # -----------------------------------------------------

    total_titles = (
        Book.objects.count()
    )


    # -----------------------------------------------------
    # MOVEMENT CHART
    # -----------------------------------------------------

    period_labels = []

    incoming_values = []

    outgoing_values = []


    for i in range(period):

        day = (
            start_date
            + timedelta(days=i)
        )


        period_labels.append(
            day.strftime(
                "%d.%m"
            )
        )


        day_incoming = (
            history
            .filter(
                created_at__date=day,
                action="ADD"
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )


        day_outgoing = (
            history
            .filter(
                created_at__date=day,
                action__in=[
                    "REMOVE",
                    "DELETE"
                ]
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )


        incoming_values.append(
            day_incoming
        )

        outgoing_values.append(
            day_outgoing
        )


    # -----------------------------------------------------
    # DISTRIBUTION EXPENSE PIE CHART
    # -----------------------------------------------------

    expense_data = (
        Book.objects
        .values(
            "category__name"
        )
        .annotate(
            total=Sum(
                "distribution_expense"
            )
        )
        .order_by(
            "category__name"
        )
    )


    expense_labels = []

    expense_values = []


    for item in expense_data:

        expense_labels.append(
            item["category__name"]
            or "No category"
        )

        expense_values.append(
            float(
                item["total"]
                or 0
            )
        )


    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        "selected_period": period,

        "incoming": incoming,

        "outgoing": outgoing,

        "total_books": total_books,

        "total_titles": total_titles,

        "period_labels": period_labels,

        "incoming_values": incoming_values,

        "outgoing_values": outgoing_values,

        "expense_labels": expense_labels,

        "expense_values": expense_values,
    }


    return render(
        request,
        "books/dashboard.html",
        context
    )

