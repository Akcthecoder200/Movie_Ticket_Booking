from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from .models import Movie, Show, Booking
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class BookingTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a test movie
        self.movie = Movie.objects.create(
            title='Test Movie',
            duration_minutes=120
        )
        
        # Create a test show
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name='Screen 1',
            date_time=timezone.now() + timedelta(days=1),
            total_seats=10
        )
        
        # Set up the API client
        self.client = APIClient()
    
    def test_book_seat_success(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
        
        # Attempt to book a seat
        url = reverse('book_seat', kwargs={'pk': self.show.pk})
        data = {'seat_number': 1}
        response = self.client.post(url, data, format='json')
        
        # Check if booking was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Booking.objects.filter(user=self.user, show=self.show, seat_number=1).exists())
    
    def test_book_same_seat_twice(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
        
        # Book seat 1 first time
        url = reverse('book_seat', kwargs={'pk': self.show.pk})
        data = {'seat_number': 1}
        self.client.post(url, data, format='json')
        
        # Attempt to book seat 1 again
        response = self.client.post(url, data, format='json')
        
        # Check that the second booking attempt fails
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cancel_booking(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
        
        # Create a booking
        booking = Booking.objects.create(
            user=self.user,
            show=self.show,
            seat_number=1,
            status=Booking.STATUS_BOOKED
        )
        
        # Cancel the booking
        url = reverse('cancel_booking', kwargs={'pk': booking.pk})
        response = self.client.post(url)
        
        # Check that the booking was cancelled
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CANCELLED)
    
    def test_cannot_cancel_other_user_booking(self):
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )
        
        # Create a booking for the other user
        booking = Booking.objects.create(
            user=other_user,
            show=self.show,
            seat_number=1,
            status=Booking.STATUS_BOOKED
        )
        
        # Authenticate as the first user
        self.client.force_authenticate(user=self.user)
        
        # Attempt to cancel the other user's booking
        url = reverse('cancel_booking', kwargs={'pk': booking.pk})
        response = self.client.post(url)
        
        # Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Booking should still be active
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_BOOKED)
