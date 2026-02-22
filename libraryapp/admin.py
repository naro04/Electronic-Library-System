from django.contrib import admin
from .models import (
    ShelfCategory, BookAuthor, LibraryBook,
    BorrowTicket, BookFeedback, ContactInbox, PageVisit
)

@admin.register(ShelfCategory)
class ShelfCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'icon_name')
    search_fields = ('label',)
    list_per_page = 20

@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name')
    search_fields = ('display_name',)
    list_per_page = 20

@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'published_year', 'total_copies', 'added_at')
    list_filter = ('category', 'language', 'published_year')
    search_fields = ('title', 'author__display_name')
    list_per_page = 25

@admin.register(BorrowTicket)
class BorrowTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'book', 'borrowed_at', 'due_at', 'returned_at')
    list_filter = ('returned_at',)
    search_fields = ('student__username', 'book__title')
    list_per_page = 30

@admin.register(BookFeedback)
class BookFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'book', 'stars', 'created_at')
    list_filter = ('stars',)
    search_fields = ('student__username', 'book__title')
    list_per_page = 30

@admin.register(ContactInbox)
class ContactInboxAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'subject', 'created_at')
    search_fields = ('full_name', 'email', 'subject')
    list_per_page = 30

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'path', 'ip', 'user', 'created_at')
    search_fields = ('path', 'ip', 'user_agent')
    list_filter = ('created_at',)
    list_per_page = 50