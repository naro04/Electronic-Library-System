from django.db import models
from django.contrib.auth.models import User

class StudentCard(models.Model):
    user = models.OneToOneField(User, verbose_name="المستخدم", on_delete=models.CASCADE, related_name='student_card')
    phone = models.CharField("رقم الهاتف", max_length=30, blank=True)
    avatar = models.ImageField("الصورة الشخصية", upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    class Meta:
        verbose_name = "بطاقة طالب"
        verbose_name_plural = "بطاقات الطلاب"

    def __str__(self):
        return self.user.username