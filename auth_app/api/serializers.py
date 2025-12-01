from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer used for user registration.

    It validates:
    - that the email address is unique
    - that 'password' and 'repeated_password' match

    On success, it creates a new Django `User` instance
    with a properly hashed password.
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def validate(self, attrs):
        """
        Object-level validation to ensure both password fields match.
        """
        password = attrs.get("password")
        repeated_password = attrs.get("repeated_password")

        if password != repeated_password:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match"}
            )
        return attrs

    def validate_email(self, value):
        """
        Ensure the provided email address is unique across all users.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        """
        Create and return a new `User` instance.

        The `repeated_password` field is removed from the data
        before creating the user record.
        """
        validated_data.pop("repeated_password")

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomObjectSerializer(TokenObtainPairSerializer):
    """
    Custom TokenObtainPairSerializer that allows login via email + password
    instead of username + password.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        """
        Remove the 'username' field that the parent class adds by default.
        """
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        """
        Validate the user by email and password, then fall back
        to the standard SimpleJWT validation with username.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Do not reveal whether email or password was wrong
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        # Delegate token creation to the original implementation
        data = super().validate({"username": user.username, "password": password})
        return data