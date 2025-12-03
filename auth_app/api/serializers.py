"""Serializers for user registration and JWT-based authentication."""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer used for user registration."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def validate(self, attrs):
        """Ensure password and repeated_password match."""
        password = attrs.get("password")
        repeated = attrs.get("repeated_password")
        if password != repeated:
            msg = "Passwords do not match."
            raise serializers.ValidationError({"repeated_password": msg})
        return attrs

    def validate_email(self, value):
        """Ensure email address is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        """Create and return a new user instance."""
        validated_data.pop("repeated_password", None)
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Token serializer that authenticates using email and password."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        """Remove username field from the default serializer."""
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        """Validate user credentials and build token payload."""
        email, password = attrs.get("email"), attrs.get("password")
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                raise ValueError
        except Exception:
            raise serializers.ValidationError("Invalid email or password.")
        data = super().validate({"username": user.username, "password": password})
        data["user"] = {"id": user.pk, "username": user.username, "email": user.email}
        return data