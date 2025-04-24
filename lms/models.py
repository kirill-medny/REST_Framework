from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255)
    preview = models.ImageField(upload_to="course_previews/", blank=True, null=True)
    description = models.TextField()

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    name = models.CharField(max_length=255)
    description = models.TextField()
    preview = models.ImageField(upload_to="lesson_previews/", blank=True, null=True)
    video_link = models.URLField()

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.name
