"""Serializers for user registration and JWT-based authentication."""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer used for user registration."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def validate(self, attrs):
        """Ensure password and confirmed_password match."""
        password = attrs.get("password")
        confirmed = attrs.get("confirmed_password")
        if password != confirmed:
            msg = "Passwords do not match."
            raise serializers.ValidationError({"confirmed_password": msg})
        return attrs

    def validate_email(self, value):
        """Ensure email address is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        """Create and return a new user instance."""
        validated_data.pop("confirmed_password", None)
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Token serializer that supports email or username login."""

    email = serializers.EmailField(required=False)

    def validate(self, attrs):
        """Validate user credentials and build token payload."""
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        if not password or not (username or email):
            msg = "Email/username and password are required."
            raise serializers.ValidationError(msg)
        user = self._get_user(email=email, username=username)
        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")
        data = super().validate({"username": user.username, "password": password})
        data["user"] = {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
        }
        return data

    def _get_user(self, *, email=None, username=None):
        """Return a user instance for the given identity or None."""
        lookup = {"email": email} if email else {"username": username}
        try:
            return User.objects.get(**lookup)
        except User.DoesNotExist:
            return None