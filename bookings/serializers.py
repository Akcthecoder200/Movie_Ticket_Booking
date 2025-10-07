from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Movie, Show, Booking

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'duration_minutes')

class ShowSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    class Meta:
        model = Show
        fields = ('id', 'movie', 'screen_name', 'date_time', 'total_seats')

class BookingSerializer(serializers.ModelSerializer):
    show = ShowSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'user', 'show', 'seat_number', 'status', 'created_at')
        read_only_fields = ('user', 'status', 'created_at')

class BookingCreateSerializer(serializers.Serializer):
    seat_number = serializers.IntegerField(min_value=1)

    def validate_seat_number(self, value):
        # show instance will be provided in view via self.context['show']
        show = self.context.get('show')
        if not show:
            raise serializers.ValidationError("Show context is required")
        if value > show.total_seats:
            raise serializers.ValidationError(f"seat_number must be between 1 and {show.total_seats}")
        return value