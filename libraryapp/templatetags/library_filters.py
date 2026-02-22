from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def book_status(book):
    if book.is_available():
        return mark_safe('<span class="text-success fw-bold">Available</span>')
    return mark_safe('<span class="text-danger fw-bold">Fully Borrowed</span>')