from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token

from users.models import Payment, User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "phone", "city", "avatar", "first_name", "last_name"]
        extra_kwargs = {"password": {"write_only": True, "required":False}}#Пароль только для записи

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)#Хэшируем пароль
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password is not None:
            instance.set_password(password)  # Хэшируем пароль
        return super().update(instance, validated_data)


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8) # Минимальная длина пароля
    password2 = serializers.CharField(write_only=True, min_length=8, label="Повторите пароль")
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password":"Пароль не совпадает"})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            email = validated_data["email"],
            password = validated_data["password"],
            first_name = validated_data.get("first_name", ""),
            last_name = validated_data.get("last_name", "")
        )
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: AuthUser) -> Token:
        token = super().get_token(user)

        token["email"] = user.email
        token["first_name"] = user.first_name

        return token


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "email", "first_name", "last_name", "phone", "city", "avatar"]

