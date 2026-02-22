from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ShelfCategory(models.Model):
    label = models.CharField("اسم التصنيف", max_length=120, unique=True)
    icon_name = models.CharField("الأيقونة", max_length=80, blank=True)

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.label


class BookAuthor(models.Model):
    display_name = models.CharField("اسم المؤلف", max_length=170)
    photo = models.ImageField("صورة المؤلف", upload_to='authors/', blank=True, null=True)
    bio = models.TextField("نبذة", blank=True)

    class Meta:
        verbose_name = "مؤلف"
        verbose_name_plural = "المؤلفون"

    def __str__(self):
        return self.display_name


class LibraryBook(models.Model):
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('AR', 'Arabic'),
        ('FR', 'French'),
        ('OT', 'Other'),
    ]

    title = models.CharField("عنوان الكتاب", max_length=240)
    cover = models.ImageField("صورة الغلاف", upload_to='books/', blank=True, null=True)

    author = models.ForeignKey(BookAuthor, verbose_name="المؤلف", on_delete=models.PROTECT, related_name='books')
    category = models.ForeignKey(ShelfCategory, verbose_name="التصنيف", on_delete=models.PROTECT, related_name='books')

    published_year = models.PositiveIntegerField("سنة النشر", default=2020)
    pages_total = models.PositiveIntegerField("عدد الصفحات", default=120)
    language = models.CharField("اللغة", max_length=2, choices=LANGUAGE_CHOICES, default='EN')

    description = models.TextField("الوصف")
    total_copies = models.PositiveIntegerField("إجمالي النسخ", default=1)
    added_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        verbose_name = "كتاب"
        verbose_name_plural = "الكتب"

    def __str__(self):
        return self.title

    def available_copies(self):
        active = BorrowTicket.objects.filter(book=self, returned_at__isnull=True).count()
        return max(self.total_copies - active, 0)

    def is_available(self):
        return self.available_copies() > 0

    def average_rating(self):
        feedbacks = self.feedbacks.all()
        if not feedbacks.exists():
            return 0
        avg = sum(x.stars for x in feedbacks) / feedbacks.count()
        return round(avg, 1)


class BorrowTicket(models.Model):
    student = models.ForeignKey(User, verbose_name="الطالب", on_delete=models.CASCADE, related_name='borrows')
    book = models.ForeignKey(LibraryBook, verbose_name="الكتاب", on_delete=models.CASCADE, related_name='borrows')

    borrowed_at = models.DateTimeField("تاريخ الاستعارة", default=timezone.now)
    due_at = models.DateTimeField("تاريخ الإرجاع المتوقع")
    returned_at = models.DateTimeField("تاريخ الإرجاع", blank=True, null=True)

    class Meta:
        ordering = ['-borrowed_at']
        verbose_name = "استعارة"
        verbose_name_plural = "الاستعارات"

    def __str__(self):
        return f"{self.student.username} -> {self.book.title}"

    def is_late(self):
        if self.returned_at:
            return self.returned_at > self.due_at
        return timezone.now() > self.due_at

    def remaining_days(self):
        if self.returned_at:
            return 0
        delta = self.due_at.date() - timezone.now().date()
        return delta.days


class BookFeedback(models.Model):
    student = models.ForeignKey(User, verbose_name="الطالب", on_delete=models.CASCADE, related_name='feedbacks')
    book = models.ForeignKey(LibraryBook, verbose_name="الكتاب", on_delete=models.CASCADE, related_name='feedbacks')

    stars = models.PositiveIntegerField("التقييم", default=5)
    comment = models.TextField("التعليق", blank=True)
    created_at = models.DateTimeField("تاريخ التقييم", auto_now_add=True)

    class Meta:
        unique_together = ('student', 'book')
        ordering = ['-created_at']
        verbose_name = "تقييم"
        verbose_name_plural = "التقييمات"

    def __str__(self):
        return f"{self.book.title} - {self.stars} stars"


class ContactInbox(models.Model):
    full_name = models.CharField("الاسم الكامل", max_length=120)
    email = models.EmailField("البريد الإلكتروني")
    subject = models.CharField("الموضوع", max_length=200)
    message = models.TextField("الرسالة")
    created_at = models.DateTimeField("تاريخ الإرسال", auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"

    def __str__(self):
        return f"{self.subject} ({self.email})"


class PageVisit(models.Model):
    path = models.CharField("المسار", max_length=400)
    ip = models.CharField("عنوان IP", max_length=60, blank=True)
    user_agent = models.TextField("User Agent", blank=True)
    user = models.ForeignKey(User, verbose_name="المستخدم", blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField("وقت الزيارة", auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "زيارة"
        verbose_name_plural = "سجل الزيارات"

    def __str__(self):
        return f"{self.path} @ {self.created_at:%Y-%m-%d %H:%M}"