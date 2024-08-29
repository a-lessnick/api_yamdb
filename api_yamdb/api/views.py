from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User

from serializers import GetTokenSerializer, SignUpSerializer


class AuthViewSet(viewsets.GenericViewSet):
    @action(methods=['POST'], detail=False, url_path='token')
    def get_token(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])
        if default_token_generator.check_token(
                user,
                data.get('confirmation_code')
        ):
            access_token = RefreshToken.for_user(user).access_token
            return Response(
                {'token': str(access_token)},
                status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_mail_confirmation_code(user, confirmation_code):
        send_mail(
            subject='Доступ к API',
            message=(
                f'{user.username}, Ваш \n'
                f'код подтверждения для доступа к API: {confirmation_code}'
            ),
            recipient_list=[user.email],
            from_email='practicum@yandex.com',
            fail_silently=True,
        )

    @action(methods=['POST'], detail=False, permission_classes=(AllowAny,), url_path='signup')
    def signup(self, request):
        user = User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        )
        if not user:
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid()
            user = serializer.save()
            confirmation_code = default_token_generator.make_token(user)
            AuthViewSet.send_mail_confirmation_code(user, confirmation_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = SignUpSerializer(user[0])
        confirmation_code = default_token_generator.make_token(user[0])
        AuthViewSet.send_mail_confirmation_code(user[0], confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)
