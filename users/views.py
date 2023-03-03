from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserValidationSerializer, UserLoginSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import random


@api_view(['POST'])
def registration_view(request):
    serializer = UserValidationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = User.objects.create_user(username=serializer.validated_data.get('username'),
                                    password=serializer.validated_data.get('password'),
                                    is_active=False)
    confirmation_code = random.randint(100000, 999999)
    user.confirm_code = confirmation_code
    user.save()
    return Response({"confirmation_code": confirmation_code}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def confirm_view(request):
    username = request.data.get('username')
    confirm_code = request.data.get('confirm_code')
    try:
        user = User.objects.get(username=username, confirm_code=confirm_code)
    except User.DoesNotExist:
        return Response({"error": "Invalid username or confirm code"}, status=status.HTTP_400_BAD_REQUEST)
    user.is_active = True
    user.confirm_code = None
    user.save()
    return Response({"message": "User registration confirmed successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def authorization_view(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(username=serializer.validated_data.get('username'),
                        password=serializer.validated_data.get('password'))

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response(data={'key': token.key})
    return Response(status=status.HTTP_401_UNAUTHORIZED)
