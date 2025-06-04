import logging

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from tasks.models import Task
from tasks.serializers import TaskSerializer


logger = logging.getLogger(name=__name__)


class TasksViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination()

    def paginate_queryset(self, queryset: QuerySet[Task]) -> list | None:
        paginator = self.pagination_class
        return paginator.paginate_queryset(
            queryset=queryset, request=self.request, view=self
        )

    def get_paginated_response(self, data: dict) -> Response:
        paginator = self.pagination_class
        return paginator.get_paginated_response(data=data)

    @swagger_auto_schema(
        responses={
            200: TaskSerializer(many=True),
            401: "Unauthorized Error"
        }
    )
    def list(self, request: Request) -> Response:
        tasks: QuerySet[Task] = Task.objects.filter(user=request.user)
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
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(user=request.user)
            return Response(
                data={"message": "Task created successfully!"},
                status=status.HTTP_201_CREATED
            )
        except Exception:
            logger.exception(msg="Error creating task")
            return Response(
                data={"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={
            200: "Success Updated!",
            400: "Validation Errors",
            401: "Unauthorized Error",
            500: "Internal server error"
        }
    )
    def update(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, user=request.user, pk=pk)
        serializer = TaskSerializer(instance=task, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response(
                data={"message": "Task updated successfully!"},
                status=status.HTTP_200_OK
            )
        except Exception:
            logger.exception(msg="Error updating task")
            return Response(
                data={"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={
            200: "Success Partial Updated!",
            400: "Validation Errors",
            401: "Unauthorized Error",
            500: "Internal server error"
        }
    )
    def partial_update(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, user=request.user, pk=pk)
        serializer = TaskSerializer(
            instance=task, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response(
                data={"message": "Task updated successfully!"},
                status=status.HTTP_200_OK
            )
        except Exception:
            logger.exception(msg="Error updating task")
            return Response(
                data={"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        responses={
            200: "Success Deleted!",
            401: "Unauthorized Error",
        }
    )
    def destroy(self, request: Request, pk: int) -> Response:
        task: Task = get_object_or_404(Task, user=request.user, pk=pk)
        task.delete()
        return Response(
            data={"message": "task deleted!"}, status=status.HTTP_200_OK
        )
