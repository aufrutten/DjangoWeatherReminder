from rest_framework import viewsets
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework import serializers, mixins, generics
from django.shortcuts import get_object_or_404, get_list_or_404

from WeatherReminder.models import User, City, Subscription
from .serializers import (UserSerializer,
                          CreateUserSerializer,
                          CitySerializer,
                          CreateCitySerializer,
                          SubscriptionSerializer,
                          CreateSubscriptionSerializer,
                          UpdateSubscriptionSerializer)

from .permissions import (AllowAny,
                          IsAdminUser,
                          IsAuthenticated,
                          IsAnonymousOnly,
                          IsOwnerOrAdmin,
                          IsOwnerOrAdminOrReadOnly,
                          IsAdminOrReadOnly)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects
    serializer_class = UserSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = CreateUserSerializer
        return serializer_class

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        if self.action == 'create':
            return [IsAnonymousOnly()]
        return [IsOwnerOrAdmin()]

    @action(detail=False, methods=['get', 'update', 'put', 'options'], permission_classes=[IsAuthenticated()])
    def me(self, request):
        if self.request.method == "PUT":
            user = UserSerializer(instance=get_object_or_404(User, email=request.user),
                                  context={'request': request},
                                  data=request.data)
            user.save() if user.is_valid() else 0
            return Response(user.data)

        user = UserSerializer(instance=get_object_or_404(User, email=request.user), context={'request': request})
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


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = CreateSubscriptionSerializer
        if self.action == 'update':
            serializer_class = UpdateSubscriptionSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):
        self.get_serializer_class()(data=request.data).is_valid(raise_exception=True)  # check validation

        user = get_object_or_404(User, email=request.user)  # getting user instance
        city, created = City.objects.get_or_create(city=request.data['city'])  # get or create city instance
        city.update_weather()  # updating weather with the rules in JSON config of APP

        subscription, created = Subscription.objects.get_or_create(user=user, city=city)  # get exist or create new subs
        subscription.frequency_update = request.data['frequency_update']  # adding frequency from user input
        subscription.save()  # saving the instance

        serializer = CitySerializer(instance=subscription)  # insert instance for JSON representation
        headers = self.get_success_headers(serializer.data)  # getting the headers
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
