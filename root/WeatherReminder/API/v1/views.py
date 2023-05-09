from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework import serializers
from django.shortcuts import get_object_or_404, get_list_or_404

from WeatherReminder.models import User, City
from .serializers import (UserSerializer,
                          CreateUserSerializer,
                          CitySerializer,
                          CreateCitySerializer)

from .permissions import (AllowAny,
                          IsAdminUser,
                          IsAuthenticated,
                          IsAnonymousOnly,
                          IsOwnerOrAdmin,
                          IsOwnerOrAdminOrReadOnly,
                          IsAdminOrReadOnly)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(email=self.request.user)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = CreateUserSerializer
        return serializer_class

    def get_permissions(self):
        if self.request.method in ("OPTIONS", "HEAD", "GET"):
            return [AllowAny()]
        if self.request.method == "POST":
            return [IsAnonymousOnly()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get', 'update', 'put', 'options'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if self.request.method == "PUT":
            user = UserSerializer(instance=get_object_or_404(User, email=request.user),
                                  context={'request': request},
                                  data=request.data)
            user.save() if user.is_valid() else 0
            return Response(user.data)

        user = UserSerializer(get_object_or_404(User, email=request.user), context={'request': request})
        return Response(user.data)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = CreateCitySerializer
        return serializer_class
