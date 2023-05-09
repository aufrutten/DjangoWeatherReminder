from django.contrib.auth.password_validation import validate_password as val_pass
from django.conf import settings
from rest_framework import serializers
from WeatherReminder.models import User, City


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')
        read_only_fields = []

    def validate_password(self, value):
        val_pass(value)
        return value

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
            del validated_data['password']
        return super().update(instance, validated_data)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(CreateUserSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta(CreateUserSerializer.Meta):
        fields = CreateUserSerializer.Meta.fields
        read_only_fields = CreateUserSerializer.Meta.read_only_fields.copy()
        fields += ('frequency_update', 'notification_is_enable', 'subscriptions')
        read_only_fields += ['email']


class CreateCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'city', 'temperature', 'humidity', 'weather', 'last_update')
        read_only_fields = ['temperature', 'humidity', 'weather', 'last_update']

    def validate_city(self, value):
        if settings.GC.get_cities_by_name(value.title()):
            return value.title()
        raise serializers.ValidationError("That city isn't exist")


class CitySerializer(CreateCitySerializer):

    class Meta(CreateCitySerializer.Meta):
        read_only_fields = CreateCitySerializer.Meta.read_only_fields.copy()
        read_only_fields += ['city']

