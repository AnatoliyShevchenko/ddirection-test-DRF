import logging

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from tasks.models import Task
from tasks.serializers import TaskSerializer, TaskQuerySerializer


logger = logging.getLogger(name=__name__)


class TasksViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination()
    create_update_responses = {
        201: "Success Created!",
        400: "Validation Errors",
        401: "Unauthorized Error",
        500: "Internal server error"
    }

    def paginate_queryset(self, queryset: QuerySet[Task]) -> list | None:
        paginator = self.pagination_class
        return paginator.paginate_queryset(
            queryset=queryset, request=self.request, view=self
        )

    def get_paginated_response(self, data: dict) -> Response:
        paginator = self.pagination_class
        return paginator.get_paginated_response(data=data)

    def create_or_update_obj(
        self,
        request: Request,
        method_name: str,
        instance: Task | None = None,
        partial: bool = False,
        status_on_success: int = status.HTTP_200_OK
    ):
        serializer = TaskSerializer(
            instance=instance, data=request.data,
            context={"request": request}, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response(
                data={"message": f"Task {method_name[:-1]}ed successfully!"},
                status=status_on_success
            )
        except Exception:
            logger.exception(msg=f"Error {method_name[:-1]}ing task")
            return Response(
                data={"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        query_serializer=TaskQuerySerializer(),
        responses={
            200: TaskSerializer(many=True),
            400: "Query Params Validation Errors",
            401: "Unauthorized Error"
        }
    )
    def list(self, request: Request) -> Response:
        query_serializer = TaskQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        filters: dict = query_serializer.validated_data

        # можно сделать так, т.к очевидно у нас есть связь Task -> User
        tasks: QuerySet[Task] = request.user.user_tasks.all()
        # Или пойти обычным путем, тут в принципе разницы нет
        #tasks: QuerySet[Task] = Task.objects.filter(user=request.user)

        title = filters.get("title")
        task_status = filters.get("status")
        sort_by = filters.get("sortBy")
        order = filters.get("order")

        if title:
            tasks = tasks.filter(title__icontains=title)
        if task_status:
            tasks = tasks.filter(status=task_status)
        if sort_by:
            ordering = sort_by if order == "asc" else f"-{sort_by}"
            tasks = tasks.order_by(ordering)

        page = self.paginate_queryset(queryset=tasks)
        if not page:
            serializer = TaskSerializer(instance=tasks, many=True)
            return Response(
                data=serializer.data, status=status.HTTP_200_OK
            )
        serializer = TaskSerializer(instance=page, many=True)
        return self.get_paginated_response(data=serializer.data)

    @swagger_auto_schema(
        responses={
            200: TaskSerializer,
            401: "Unauthorized Error",
            404: "Object not found"
        }
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(
            Task, user=request.user, pk=pk
        )
        serializer = TaskSerializer(instance=task)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={
            201: "Success Created!",
            400: "Validation Errors",
            401: "Unauthorized Error",
            500: "Internal server error"
        }
    )
    def create(self, request: Request) -> Response:
        return self.create_or_update_obj(
            request=request, method_name="create",
            status_on_success=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={
            201: "Success Created!",
            400: "Validation Errors",
            401: "Unauthorized Error",
            404: "Not found error",
            500: "Internal server error"
        }
    )
    def update(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, user=request.user, pk=pk)
        return self.create_or_update_obj(
            request=request, instance=task, method_name="update"
        )

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={
            201: "Success Created!",
            400: "Validation Errors",
            401: "Unauthorized Error",
            404: "Not found error",
            500: "Internal server error"
        }
    )
    def partial_update(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, user=request.user, pk=pk)
        return self.create_or_update_obj(
            request=request, method_name="partial update", instance=task, partial=True
        )

    @swagger_auto_schema(
        responses={
            200: "Success Deleted!",
            401: "Unauthorized Error",
            404: "Not found error"
        }
    )
    def destroy(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, user=request.user, pk=pk)
        task.delete()
        return Response(
            data={"message": "task deleted!"}, status=status.HTTP_200_OK
        )
