from django.db import models
from django.contrib.auth.models import User


class Status(models.TextChoices):
    NEW = "new", "новая"
    IN_PROGRESS = "in_progress", "выполняется"
    DONE = "done", "готова"

class Task(models.Model):
    title = models.CharField(
        verbose_name="заголовок",
        max_length=200
    )
    description = models.TextField(
        verbose_name="описание задачи"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="user_tasks"
    )
    due_date = models.DateField(
        verbose_name="дедлайн"
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "задача"
        verbose_name_plural = "задачи"

    def __str__(self):
        return f"{self.title} -> {self.user} -> {self.status}"
