from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from .models import LibraryBook, ShelfCategory, BookAuthor, BorrowTicket, BookFeedback
from .forms import ContactForm, FeedbackForm
from accountsapp.models import StudentCard

MAX_ACTIVE_BORROWS = 5
BORROW_DAYS = 14


def home(request):
    latest_books = LibraryBook.objects.all()[:6]

    rated = LibraryBook.objects.annotate(cnt=Count('feedbacks')).filter(cnt__gt=0)
    top_rated = sorted(rated, key=lambda b: b.average_rating(), reverse=True)[:3]

    stats = {
        "books": LibraryBook.objects.count(),
        "authors": BookAuthor.objects.count(),
        "students": User.objects.filter(is_staff=False).count(),
    }

    return render(request, "libraryapp/home.html", {
        "latest_books": latest_books,
        "top_rated": top_rated,
        "stats": stats
    })


def books(request):
    keyword = request.GET.get("q", "").strip()
    category_id = request.GET.get("c", "").strip()
    sort_mode = request.GET.get("sort", "new")

    queryset = LibraryBook.objects.select_related("author", "category").all()

    if keyword:
        queryset = queryset.filter(Q(title__icontains=keyword) | Q(author__display_name__icontains=keyword))

    if category_id:
        queryset = queryset.filter(category__id=category_id)

    if sort_mode == "old":
        queryset = queryset.order_by("added_at")
    elif sort_mode == "rating":
        queryset = list(queryset)
        queryset.sort(key=lambda b: b.average_rating(), reverse=True)
    else:
        queryset = queryset.order_by("-added_at")

    categories = ShelfCategory.objects.all()

    paginator = Paginator(queryset, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "libraryapp/books.html", {
        "page_obj": page_obj,
        "categories": categories,
        "q": keyword,
        "c": category_id,
        "sort": sort_mode
    })


def book_detail(request, book_id):
    book = get_object_or_404(LibraryBook.objects.select_related("author", "category"), pk=book_id)

    guest = not request.user.is_authenticated
    borrowed_by_me_now = False
    borrowed_before = False

    if request.user.is_authenticated:
        borrowed_by_me_now = BorrowTicket.objects.filter(
            student=request.user, book=book, returned_at__isnull=True
        ).exists()

        borrowed_before = BorrowTicket.objects.filter(
            student=request.user, book=book, returned_at__isnull=False
        ).exists()

    feedbacks = book.feedbacks.select_related("student").all()


    for f in feedbacks:
        StudentCard.objects.get_or_create(user=f.student)

    return render(request, "libraryapp/book_detail.html", {
        "book": book,
        "guest": guest,
        "borrowed_by_me_now": borrowed_by_me_now,
        "borrowed_before": borrowed_before,
        "feedbacks": feedbacks
    })


def categories(request):
    all_categories = ShelfCategory.objects.annotate(total=Count("books")).all()
    return render(request, "libraryapp/categories.html", {"categories": all_categories})


def authors(request):
    all_authors = BookAuthor.objects.annotate(total=Count("books")).all()
    return render(request, "libraryapp/authors.html", {"authors": all_authors})


def author_detail(request, author_id):
    author = get_object_or_404(BookAuthor, pk=author_id)
    books = LibraryBook.objects.select_related("category").filter(author=author).order_by("-added_at")
    return render(request, "libraryapp/author_detail.html", {"author": author, "books": books})


def contact(request):
    form = ContactForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your message has been sent successfully.")
        return redirect("contact")

    return render(request, "libraryapp/contact.html", {"form": form})


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(LibraryBook, pk=book_id)

    if not book.is_available():
        messages.error(request, "No copies available at the moment.")
        return redirect("book_detail", book_id=book.id)

    already_active = BorrowTicket.objects.filter(student=request.user, book=book, returned_at__isnull=True).exists()
    if already_active:
        messages.warning(request, "You already borrowed this book.")
        return redirect("book_detail", book_id=book.id)

    active_count = BorrowTicket.objects.filter(student=request.user, returned_at__isnull=True).count()
    if active_count >= MAX_ACTIVE_BORROWS:
        messages.error(request, f"You can borrow up to {MAX_ACTIVE_BORROWS} books only.")
        return redirect("book_detail", book_id=book.id)


    if request.method == "GET":
        return render(request, "libraryapp/borrow_confirm.html", {"book": book})

    due = timezone.now() + timedelta(days=BORROW_DAYS)
    BorrowTicket.objects.create(student=request.user, book=book, due_at=due)

    messages.success(request, "Book borrowed successfully.")
    return redirect("my_borrows")


@login_required
def my_borrows(request):
    active = BorrowTicket.objects.select_related("book").filter(student=request.user, returned_at__isnull=True)
    history = BorrowTicket.objects.select_related("book").filter(student=request.user, returned_at__isnull=False)
    return render(request, "libraryapp/my_borrows.html", {"borrows": active, "history": history})


@login_required
def return_book(request, borrow_id):
    borrow = get_object_or_404(BorrowTicket, pk=borrow_id, student=request.user)

    if borrow.returned_at:
        messages.info(request, "This borrow is already closed.")
        return redirect("my_borrows")

    borrow.returned_at = timezone.now()
    borrow.save()

    messages.success(request, "Book returned successfully.")
    return redirect("my_borrows")


@login_required
def add_review(request, book_id):
    book = get_object_or_404(LibraryBook, pk=book_id)

    has_borrowed_before = BorrowTicket.objects.filter(
        student=request.user, book=book, returned_at__isnull=False
    ).exists()

    if not has_borrowed_before:
        messages.error(request, "You can review a book only after borrowing it before.")
        return redirect("book_detail", book_id=book.id)

    if BookFeedback.objects.filter(student=request.user, book=book).exists():
        messages.warning(request, "You already reviewed this book.")
        return redirect("book_detail", book_id=book.id)

    form = FeedbackForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.student = request.user
        review.book = book

        if not (1 <= review.stars <= 5):
            messages.error(request, "Rating must be between 1 and 5.")
            return redirect("add_review", book_id=book.id)

        review.save()
        messages.success(request, "Review added successfully.")
        return redirect("book_detail", book_id=book.id)

    return render(request, "libraryapp/add_review.html", {"book": book, "form": form})