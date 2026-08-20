import time
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from apps.testapp.models import CustomUser

@shared_task
def send_lesson_notification(lesson_id, lesson_title):
    # Имитация задержки работы почтового сервера
    time.sleep(3)
    
    # Находим всех активных студентов
    students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT, is_active=True)
    student_emails = list(students.values_list('email', flat=True))
    
    if not student_emails:
        return "Нет студентов для отправки уведомлений"
        
    subject = f"Новый урок: {lesson_title}"
    message = f"Здравствуйте!\n\nДобавлен новый урок: {lesson_title} (ID: {lesson_id}).\n\nПриятного обучения!"
    
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com'
    
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=student_emails,
        fail_silently=False,
    )
    
    return f"Уведомления отправлены {len(student_emails)} студентам."
