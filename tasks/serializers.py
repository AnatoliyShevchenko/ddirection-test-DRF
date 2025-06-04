from django.utils import timezone
from rest_framework import serializers

from tasks.models import Task, Status


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField(
        method_name="get_is_overdue"
    )

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status",
            "user", "due_date", "is_overdue"
        ]
        read_only_fields = ["id", "is_overdue", "user"]

    def get_is_overdue(self, obj) -> bool:
        return (
            obj.due_date < timezone.now().date()
            and obj.status != Status.DONE
        )
