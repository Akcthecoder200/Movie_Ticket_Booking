# Movie Ticket Booking System

A Django REST API for booking movie tickets, managing shows, and users.

This project was built using Python, Django, and Django REST Framework to create a complete Movie Ticket Booking System API with JWT authentication and Swagger documentation.

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

**Documentation:**

- Comprehensive API documentation is available through Swagger UI at:
  - http://127.0.0.1:8000/swagger/
- This interactive documentation allows you to explore and test all endpoints directly from your browser.

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

### Step-by-Step JWT Authentication Guide:

1. First, obtain a token by making a POST request to `/api/login/` with your credentials:

   ```json
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

2. The response will contain an access token and a refresh token:

   ```json
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
   }
   ```

3. For all authenticated API requests, include the access token in the Authorization header:

   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
   ```

4. When the access token expires (after 60 minutes), use the refresh token to get a new one:
   ```
   POST /api/token/refresh/
   {
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
   }
   ```

You can also use the Swagger UI "Authorize" button and input `Bearer <access_token>` to authenticate all requests made through the Swagger interface.

## Business Rules

- Prevents double booking via database constraints and existence checks
- Prevents overbooking by comparing booked seats with total available seats
- Canceled bookings free up seats for new bookings
- Security checks ensure users can only manage their own bookings

## Concurrency Handling

- Uses database transactions with row-level locking via `select_for_update()` to prevent race conditions
- Catches integrity errors for safety against edge case race conditions

## Project Structure

The project follows a standard Django structure:

```
moviebooking/           # Main project directory
├── moviebooking/       # Project settings
│   ├── settings.py     # Django settings
│   ├── urls.py         # Root URL configuration
│   └── ...
├── bookings/           # Main application
│   ├── models.py       # Database models
│   ├── serializers.py  # REST API serializers
│   ├── views.py        # API endpoints
│   ├── urls.py         # API URL routes
│   ├── admin.py        # Admin interface config
│   └── tests.py        # Automated tests
├── manage.py           # Django management script
└── requirements.txt    # Project dependencies
```

## Running Tests

```bash
python manage.py test
```

## Verifying All Features

Follow these steps to manually verify that all features are working correctly:

### 1. Create Test Data

1. Start the server:

   ```bash
   python manage.py runserver
   ```

2. Go to the admin panel: http://127.0.0.1:8000/admin/
3. Login with your superuser credentials (username: admin)
4. Create test data:
   - Add 2-3 Movies (e.g., "Avengers", "Jurassic Park")
   - For each movie, add 1-2 Shows with different times and seat counts

### 2. Test User Registration and Authentication

#### Register a New User

1. Using Swagger UI (http://127.0.0.1:8000/swagger/), navigate to `/api/signup/` endpoint
2. Click "Try it out" and enter:
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "strongpassword123"
   }
   ```
3. You should receive a 201 Created response with user details

#### Login to Get JWT Token

1. Navigate to `/api/login/` endpoint in Swagger
2. Enter the credentials:
   ```json
   {
     "username": "testuser",
     "password": "strongpassword123"
   }
   ```
3. You'll receive access and refresh tokens
4. In Swagger, click the "Authorize" button at the top and enter:
   ```
   Bearer your_access_token_here
   ```
   This will authenticate all subsequent requests

### 3. Test Movie and Show Listing

#### List All Movies

1. Navigate to `/api/movies/` endpoint
2. Execute the GET request
3. Verify you see all the movies you created in the admin panel

#### List Shows for a Movie

1. Navigate to `/api/movies/{id}/shows/` endpoint
2. Enter a movie ID from the previous response
3. Verify you see all shows for that movie

### 4. Test Booking Functionality

#### Book a Seat

1. Navigate to `/api/shows/{id}/book/` endpoint
2. Enter a show ID from the previous steps
3. In the request body, enter:
   ```json
   {
     "seat_number": 1
   }
   ```
4. Execute the request - you should get a 201 Created response

#### View Your Bookings

1. Navigate to `/api/my-bookings/` endpoint
2. Execute the GET request
3. Verify you see the booking you just created

#### Cancel a Booking

1. Navigate to `/api/bookings/{id}/cancel/` endpoint
2. Enter the booking ID from the previous response
3. Execute the POST request
4. You should get a 200 OK response
5. Verify the booking status is now "cancelled" by checking your bookings again

### 5. Test Business Rules

#### Test Double Booking Prevention

1. Try to book the same seat number for the same show again
2. You should receive a 400 Bad Request error

#### Test Overbooking Prevention

1. Create a show with a small number of seats (e.g., 2)
2. Book all available seats
3. Try to book one more seat - it should fail with a 400 error

#### Test Security Checks

1. Register a second user and get their JWT token
2. Try to cancel the first user's booking using the second user's token
3. This should fail with a 403 Forbidden error

### 6. Testing via curl (Alternative)

If you prefer using curl commands:

#### Register a User

```bash
curl -X POST http://127.0.0.1:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"strongpass"}'
```

#### Login

```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"strongpass"}'
```

#### Book a Seat

```bash
curl -X POST http://127.0.0.1:8000/api/shows/1/book/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"seat_number":5}'
```

### 7. Running Automated Tests

The project includes tests that verify core functionality:

```bash
python manage.py test
```

If all tests pass, it confirms that the key features are working as expected.

## GitHub Repository

This project is available on GitHub at: https://github.com/Akcthecoder200/Movie_Ticket_Booking

The repository contains:

- Complete Django project code
- requirements.txt with all dependencies
- This comprehensive README.md with setup instructions and usage guidelines

To clone this repository:

```bash
git clone https://github.com/Akcthecoder200/Movie_Ticket_Booking.git
cd Movie_Ticket_Booking
```
