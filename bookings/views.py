from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Movie, Show, Booking
from .serializers import (
    SignupSerializer, MovieSerializer, ShowSerializer,
    BookingSerializer, BookingCreateSerializer
)

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = (permissions.AllowAny,)

# Use TokenObtainPairView for /login/ (it returns access & refresh tokens)
# in urls map TokenObtainPairView to /login/

class MoviesListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (permissions.AllowAny,)

class MovieShowsListView(generics.ListAPIView):
    serializer_class = ShowSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        movie_id = self.kwargs['pk']
        return Show.objects.filter(movie_id=movie_id)

class BookSeatView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        """
        POST /shows/<id>/book/  body: { "seat_number": 5 }
        """
        show = get_object_or_404(Show, pk=pk)
        serializer = BookingCreateSerializer(data=request.data, context={'show': show})
        serializer.is_valid(raise_exception=True)
        seat_number = serializer.validated_data['seat_number']

        # Use DB transaction + select_for_update to serialize booking attempts for this show
        try:
            with transaction.atomic():
                # Lock the show row to prevent race conditions on the same show
                show_locked = Show.objects.select_for_update().get(pk=show.pk)

                # Check if seat already booked
                existing = Booking.objects.filter(show=show_locked, seat_number=seat_number, status=Booking.STATUS_BOOKED).exists()
                if existing:
                    return Response({"detail": "Seat already booked."}, status=status.HTTP_400_BAD_REQUEST)

                # Check capacity (count only booked seats)
                booked_count = Booking.objects.filter(show=show_locked, status=Booking.STATUS_BOOKED).count()
                if booked_count >= show_locked.total_seats:
                    return Response({"detail": "Show is fully booked."}, status=status.HTTP_400_BAD_REQUEST)

                # Create booking
                try:
                    booking = Booking.objects.create(
                        user=request.user,
                        show=show_locked,
                        seat_number=seat_number,
                        status=Booking.STATUS_BOOKED
                    )
                except IntegrityError:
                    # unique constraint hit — another transaction booked same seat
                    return Response({"detail": "Seat already booked (race)." }, status=status.HTTP_409_CONFLICT)

        except Show.DoesNotExist:
            return Response({"detail": "Show not found."}, status=status.HTTP_404_NOT_FOUND)

        out = BookingSerializer(booking)
        return Response(out.data, status=status.HTTP_201_CREATED)

class CancelBookingView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        if booking.user != request.user:
            return Response({"detail": "You cannot cancel another user's booking."}, status=status.HTTP_403_FORBIDDEN)
        if booking.status == Booking.STATUS_CANCELLED:
            return Response({"detail": "Booking already cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = Booking.STATUS_CANCELLED
        booking.save()
        return Response({"detail": "Booking cancelled."}, status=status.HTTP_200_OK)

class MyBookingsListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')
