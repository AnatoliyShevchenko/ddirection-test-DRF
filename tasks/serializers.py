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

    def validate_title(self, value):
        user = self.context["request"].user
        if Task.objects.filter(title=value, user=user).exclude(
            status=Status.DONE).exists():
            raise serializers.ValidationError(
                "You're already have incomplete task with this title!"
            )
        return value

    def validate_status(self, value):
        if self.instance is None and value != Status.NEW:
            raise serializers.ValidationError(
                "You should create task with status 'new'"
            )
        return value

    def validate_due_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Due date cannot be in the past."
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        return Task.objects.create(user=user, **validated_data)

class TaskQuerySerializer(serializers.Serializer):
    """Serializer for validation filters."""

    title = serializers.CharField(
        max_length=50, required=False
    )
    status = serializers.ChoiceField(
        choices=Status.choices, required=False
    )
    order = serializers.ChoiceField(
        choices=["asc", "desc"], required=False
    )
    sortBy = serializers.ChoiceField(
        choices=["due_date"], required=False
    )

    def validate(self, attrs):
        order = attrs.get("order")
        sort_by = attrs.get("sortBy")

        if order and not sort_by:
            raise serializers.ValidationError({
                "sortBy": "This field is required when 'order' is provided."
            })
        if sort_by and not order:
            raise serializers.ValidationError({
                "order": "This field is required when 'sortBy' is provided."
            })
        return attrs
