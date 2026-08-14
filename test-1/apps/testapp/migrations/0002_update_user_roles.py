from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("testapp", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[("student", "Студент"), ("teacher", "Преподаватель")],
                default="student",
                max_length=20,
            ),
        ),
    ]
