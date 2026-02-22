from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('books/', views.books, name='books'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),

    path('categories/', views.categories, name='categories'),
    path('authors/', views.authors, name='authors'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),

    path('contact/', views.contact, name='contact'),

    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('my-books/', views.my_borrows, name='my_borrows'),
    path('return/<int:borrow_id>/', views.return_book, name='return_book'),

    path('book/<int:book_id>/review/', views.add_review, name='add_review'),
]