from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response

from apps.lessons.models import Lesson
from apps.lessons.serializers import LessonSerializer
from apps.lessons.permissions import IsTeacherOrReadOnly
from apps.lessons.tasks import send_lesson_notification

LESSONS_LIST_CACHE_KEY = 'lessons_list'
LESSONS_LIST_CACHE_TTL = 300        # 5 минут

LESSON_DETAIL_KEY = 'lesson_detail_{}'
LESSON_DETAIL_TTL = 600             # 10 минут

LESSON_VIEWS_KEY = 'lesson_views_{}'

class LessonCreateAPIView(generics.CreateAPIView):
    """
    POST /api/v1/lessons/create/ — создание урока (только teacher) с уведомлением через Celery
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        lesson = serializer.instance
        
        # Сбрасываем кэш списка уроков
        cache.delete(LESSONS_LIST_CACHE_KEY)
        
        # Вызов задачи Celery для отправки уведомлений
        send_lesson_notification.delay(lesson.id, lesson.title)
        
        return Response(
            {"message": "Урок создан, уведомления отправляются"},
            status=status.HTTP_201_CREATED
        )


class LessonListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/lessons/ — список уроков (кэш Redis 5 мин)
    POST /api/v1/lessons/ — создание урока (только teacher)
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def list(self, request, *args, **kwargs):
        # Пробуем достать из Redis
        cached_data = cache.get(LESSONS_LIST_CACHE_KEY)
        if cached_data is not None:
            return Response(cached_data)

        # Если нет в кэше — берём из БД
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Записываем в Redis на 300 сек
        cache.set(LESSONS_LIST_CACHE_KEY, data, LESSONS_LIST_CACHE_TTL)
        return Response(data)

    def perform_create(self, serializer):
        serializer.save()
        # Сбрасываем кэш списка уроков
        cache.delete(LESSONS_LIST_CACHE_KEY)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/lessons/<id>/ — детали урока + инкремент просмотров
    PUT    /api/v1/lessons/<id>/ — обновление урока (только teacher)
    PATCH  /api/v1/lessons/<id>/ — частичное обновление (только teacher)
    DELETE /api/v1/lessons/<id>/ — удаление урока (только teacher)
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        views_key = LESSON_VIEWS_KEY.format(instance.pk)
        detail_key = LESSON_DETAIL_KEY.format(instance.pk)

        # --- Атомарный инкремент просмотров ---
        try:
            current_views = cache.incr(views_key)
        except ValueError:
            # Ключ не существует — инициализируем из БД и инкрементируем
            cache.set(views_key, instance.view_count + 1)
            current_views = instance.view_count + 1

        # --- Кэш деталей урока ---
        cached_data = cache.get(detail_key)
        if cached_data is not None:
            # Подставляем актуальный счётчик просмотров из Redis
            cached_data['view_count'] = current_views
            return Response(cached_data)

        # Если нет в кэше — сериализуем из БД
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['view_count'] = current_views

        # Сохраняем в Redis на 600 сек
        cache.set(detail_key, data, LESSON_DETAIL_TTL)
        return Response(data)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Синхронизируем view_count из Redis в БД перед сбросом кэша
        views_key = LESSON_VIEWS_KEY.format(instance.pk)
        redis_views = cache.get(views_key)
        if redis_views is not None:
            instance.view_count = int(redis_views)
            instance.save(update_fields=['view_count'])
        # Сбрасываем кэш деталей и списка
        cache.delete(LESSON_DETAIL_KEY.format(instance.pk))
        cache.delete(LESSONS_LIST_CACHE_KEY)

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        # Сбрасываем все связанные ключи
        cache.delete(LESSON_DETAIL_KEY.format(pk))
        cache.delete(LESSON_VIEWS_KEY.format(pk))
        cache.delete(LESSONS_LIST_CACHE_KEY)
