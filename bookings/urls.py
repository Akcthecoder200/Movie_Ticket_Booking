from django.urls import path
from .views import (
    SignupView, MoviesListView, MovieShowsListView,
    BookSeatView, CancelBookingView, MyBookingsListView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('movies/', MoviesListView.as_view(), name='movies_list'),
    path('movies/<int:pk>/shows/', MovieShowsListView.as_view(), name='movie_shows'),
    path('shows/<int:pk>/book/', BookSeatView.as_view(), name='book_seat'),

    path('bookings/<int:pk>/cancel/', CancelBookingView.as_view(), name='cancel_booking'),
    path('my-bookings/', MyBookingsListView.as_view(), name='my_bookings'),
]