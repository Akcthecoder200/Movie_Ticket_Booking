# Movie Ticket Booking System

A Django REST API for booking movie tickets, managing shows, and users.

## Tech Stack

- Python 3.9+
- Django
- Django REST Framework
- djangorestframework-simplejwt (JWT Authentication)
- drf-yasg (Swagger/OpenAPI Documentation)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd Movie_booking
```

2. Create a virtual environment and activate it:
```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser (for admin access):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The API will be available at http://127.0.0.1:8000/api/
Swagger documentation is available at http://127.0.0.1:8000/swagger/

## API Endpoints

### Authentication
- `POST /api/signup/` - Register a new user
- `POST /api/login/` - Get JWT tokens (access & refresh)
- `POST /api/token/refresh/` - Refresh access token

### Movies & Shows
- `GET /api/movies/` - List all movies
- `GET /api/movies/{id}/shows/` - List shows for a specific movie

### Bookings
- `POST /api/shows/{id}/book/` - Book a seat (requires authentication)
  ```json
  { "seat_number": 5 }
  ```
- `GET /api/my-bookings/` - List user's bookings (requires authentication)
- `POST /api/bookings/{id}/cancel/` - Cancel a booking (requires authentication)

## Using JWT Authentication

After logging in, include the JWT token in your API requests:
```
Authorization: Bearer <access_token>
```

You can also use the Swagger UI "Authorize" button and input `Bearer <access_token>` to authenticate.

## Business Rules

- Prevents double booking via database constraints and existence checks
- Prevents overbooking by comparing booked seats with total available seats
- Canceled bookings free up seats for new bookings
- Security checks ensure users can only manage their own bookings

## Concurrency Handling

- Uses database transactions with row-level locking via `select_for_update()` to prevent race conditions
- Catches integrity errors for safety against edge case race conditions

## Running Tests

```bash
python manage.py test
```