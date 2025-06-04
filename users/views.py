import logging

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from users.serializers import UserSerializer


logger = logging.getLogger(name=__name__)


class UsersViewSet(ViewSet):
    """
    ViewSet for handling Users' objects.
    For now it's just registration,
    but in perspective we should implement all methods.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: "User created successfully",
            400: "Validation errors",
            500: "Internal server error"
        }
    )
    def create(self, request: Request) -> Response:
        """
        Handle user registration.

        Validation errors are raised by the serializer and automatically
        return HTTP 400 responses. This method catches any unexpected exceptions
        (not explicitly handled) to prevent server crashes and return a generic
        HTTP 500 response with a friendly error message.

        We do not catch specific exceptions like IntegrityError here, assuming
        validation covers common client errors. This keeps the code simpler
        for now.

        Args:
        request (Request): Incoming registration request data.

        Returns:
        Response: Success message with HTTP 201 or error message with HTTP 500.
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response(
                data={"message": "User created successfully!"},
                status=status.HTTP_201_CREATED
            )
        except Exception:
            logger.exception(msg="Error creating user")
            return Response(
                data={"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
