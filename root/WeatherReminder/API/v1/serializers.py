from django.contrib.auth.password_validation import validate_password as val_pass
from django.conf import settings
from rest_framework import serializers


from WeatherReminder.models import User, City, Subscription


def validate_city_func(value):
    if settings.GC.get_cities_by_name(value.title().strip()):
        return value.title().strip()
    raise serializers.ValidationError("That city isn't exist")


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
        fields += ('token', 'refresh_token')
        read_only_fields += ['email', 'token', 'refresh_token']


class CreateCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'city', 'temperature', 'humidity', 'weather', 'last_update')
        read_only_fields = ['temperature', 'humidity', 'weather', 'last_update']

    def validate_city(self, value):
        return validate_city_func(value)


class CitySerializer(CreateCitySerializer):

    class Meta(CreateCitySerializer.Meta):
        read_only_fields = CreateCitySerializer.Meta.read_only_fields.copy()
        read_only_fields += ['city']


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    city = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Subscription
        fields = ('city', 'user', 'frequency_update')
        read_only_fields = ['user']

    def validate_city(self, value):
        validate_city_func(value)


class UpdateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'city', 'user', 'frequency_update')
        read_only_fields = ['id', 'city', 'user']


class SubscriptionSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Subscription
        fields = ('id', 'city', 'frequency_update')
