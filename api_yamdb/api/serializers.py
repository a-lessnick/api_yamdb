from rest_framework import serializers

from reviews.models import User


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        validators=User.REGEX_SIGNS
    )
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')
