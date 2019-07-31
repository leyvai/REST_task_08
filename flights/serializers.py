from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date
from .models import Flight, Booking, Profile


class FlightSerializer(serializers.ModelSerializer):
	class Meta:
		model = Flight
		fields = ['destination', 'time', 'price', 'id']


class BookingSerializer(serializers.ModelSerializer):
	flight = serializers.SlugRelatedField(read_only=True, slug_field='destination')
	class Meta:
		model = Booking
		fields = ['flight', 'date', 'id']


class AdminUpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['date', 'passengers']


class UpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['passengers']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        new_user = User(username=username, first_name=first_name, last_name=last_name)
        new_user.set_password(password)
        new_user.save()
        return validated_data


class UsernameSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
	tier = serializers.SerializerMethodField()
	pastbookings = serializers.SerializerMethodField()
	user = UsernameSerializer()
	class Meta:
		model = Profile
		fields = ['user', 'miles', 'pastbookings', 'tier']

	def get_pastbookings(self,obj):
		previous = obj.user.bookings.filter(date__lte=date.today())			
		return BookingSerializer(previous, many=True).data 

	def get_tier(self,obj):
		if obj.miles < 10000:
			return "Blue"
		elif obj.miles < 60000:
			return "Silver"
		elif obj.miles < 100000:
			return "Gold"
		return "Platinum"

class BookingDetailsSerializer(serializers.ModelSerializer):
	flight = FlightSerializer()
	cost = serializers.SerializerMethodField()
	class Meta:
		model = Booking
		fields = ['flight', 'date', 'passengers', 'id', 'cost']

	def get_cost(self,obj):
		return obj.passengers * obj.flight.price
