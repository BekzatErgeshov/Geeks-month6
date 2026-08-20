from rest_framework import serializers
from apps.lessons.models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'description', 'view_count', 'created_at')
