from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TasksAdmin(admin.ModelAdmin):
    model = Task
    list_display = (
        "title", "description", "status", "user", "due_date"
    )
    list_filter = ("title", "status", "due_date")
    search_fields = ("title", "user")
