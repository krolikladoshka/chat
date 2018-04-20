from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class SignUpSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(
        min_length=3, max_length=255, required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'nickname', 'password',
            'token',
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        min_length=3, max_length=255
    )
    password = serializers.CharField(min_length=8, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate_nickname(self, value):
        if not value:
            raise serializers.ValidationError('A nickname is required to login')
        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError('A password is required to login')
        return value

    def validate(self, data):
        nickname = data.pop('nickname')
        password = data.pop('password')

        user = authenticate(username=nickname, password=password)

        if user is None or not user.is_active:
            raise serializers.ValidationError('A user with this nickname/password was not found')

        return {
            'nickname': nickname,
            'password': password,
            'token': user.token,
        }


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = [
            'nickname', 'password', 'token',
            'is_staff', 'created_datetime',
        ]
        read_only_fields = [
            'token',
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop('password')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password is not None:
            instance.set_password(password)
        instance.save()

        return instance
