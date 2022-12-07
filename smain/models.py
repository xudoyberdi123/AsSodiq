from django.db import models


# Create your models here.


class DefaultDate(models.Model):
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        abstract = True
        verbose_name = "default_date"


class Course(DefaultDate):
    email = models.CharField(max_length=256)
    order_id = models.CharField(max_length=128)
    action = models.CharField(max_length=256)
    amount = models.CharField(max_length=128)
    key = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.email} {self.order_id}"
