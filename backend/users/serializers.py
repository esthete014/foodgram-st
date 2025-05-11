from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.authtoken.models import Token
from .models import User
from recipes.fields import Base64ImageField
import logging
import re
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "password")

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )
        read_only_fields = ("id", "is_subscribed")

    def get_is_subscribed(self, obj):
        request = self.context.get("request")

        if (
            not request
            or not hasattr(request, "user")
            or not request.user.is_authenticated
        ):
            return False

        current_user = request.user
        if current_user.is_anonymous:
            return False

        if (
            not hasattr(obj, "pk")
            or not obj.pk
            or (hasattr(obj, "is_anonymous") and obj.is_anonymous)
        ):
            return False

        return obj.subscribers.filter(user=current_user).exists()

    def to_representation(self, instance):
        if isinstance(instance, AnonymousUser):
            return {
                "id": None,
                "username": instance.username,
                "email": None,
                "first_name": None,
                "last_name": None,
                "avatar": None,
                "is_subscribed": False,
            }
        representation = super().to_representation(instance)
        if "avatar" not in representation or representation["avatar"] == "":
            representation["avatar"] = None
        return representation


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, obj):
        from recipes.serializers import RecipeMinifiedSerializer

        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit") if request else None
        recipes_queryset = obj.recipes.all()
        if limit:
            try:
                recipes_queryset = recipes_queryset[: int(limit)]
            except ValueError:
                pass
        return RecipeMinifiedSerializer(
            recipes_queryset, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ("avatar",)


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email")
    password = serializers.CharField(
        label="Password", style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        logger.info(f"Attempting to authenticate user with email: {email}")

        if email and password:
            try:
                user = User.objects.get(email=email)
                logger.info(f"Found user: {user.email}, checking password")
                if user.check_password(password):
                    logger.info("Password check successful")
                    attrs["user"] = user
                    return attrs
                else:
                    logger.info("Password check failed")
            except User.DoesNotExist:
                logger.info(f"No user found with email: {email}")

            msg = "Unable to log in with provided credentials."
            raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code="authorization")
