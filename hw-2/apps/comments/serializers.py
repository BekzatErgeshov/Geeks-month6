from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    # Автор проставляется автоматически во вьюшке (perform_create),
    # поэтому в ответе отдаём его email и запрещаем изменять через API.
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'text', 'created_at')
        read_only_fields = ('created_at',)
