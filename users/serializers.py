from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: dict):
        return User.objects.create_user(**validated_data)

    def validate_username(self, value: str):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует."
            )
        if " " in value:
            raise serializers.ValidationError(
                "Имя пользователя не должно содержать пробелы."
            )
        return value

    def validate_email(self, value: str):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже зарегистрирован."
            )
        return value

    def validate_password(self, value: str):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Пароль должен содержать минимум 8 символов."
            )
        if value.isdigit() or value.isalpha():
            raise serializers.ValidationError(
                "Пароль должен содержать буквы и цифры."
            )
        return value

    def validate(self, attrs: dict):
        username = attrs.get("username", "")
        email = attrs.get("email", "")
        if username and email and \
        (username == email or username in email):
            raise serializers.ValidationError(
                "Имя пользователя не должно совпадать или входить в email."
            )
        return attrs
