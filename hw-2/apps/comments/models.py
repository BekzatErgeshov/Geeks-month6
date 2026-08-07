from django.conf import settings
from django.db import models


class Comment(models.Model):
    post = models.ForeignKey(
        'testapp.Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Статья',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f'{self.author}: {self.text[:50]}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created_at',)
