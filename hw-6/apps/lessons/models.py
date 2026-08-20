from django.db import models


class Lesson(models.Model):
    title = models.CharField("Название урока", max_length=255)
    content = models.TextField("Содержимое урока", blank=True)
    view_count = models.PositiveIntegerField("Просмотры", default=0)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ("-created_at",)
