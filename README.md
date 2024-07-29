# Social Media Backend API

## Overview
This project is a FastAPI-based backend for a social media application. It provides a robust API supporting user authentication, post creation and management, commenting, liking, and user following functionality.

## Features
- User registration and authentication
- Create, read, update, and delete posts
- Comment on posts
- Like posts and comments
- Follow/unfollow users
- Search functionality for users and posts
- View count tracking for posts

## Tech Stack
- FastAPI: Modern, fast (high-performance) web framework for building APIs with Python
- SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM) library
- Pydantic: Data validation and settings management using Python type annotations
- MySQL: Relational database for data storage
- JWT: JSON Web Tokens for secure authentication

## Prerequisites
- Python 3.7+
- MySQL

## Setup and Installation

1. Clone the repository:
   git clone https://github.com/abcd/social-media-backend.git
   cd social-media-backend

2. Set up a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install dependencies:
   pip install -r requirements.txt

4. Set up environment variables:
   - Copy the .env.example file to a new file named .env:
     cp .env.example .env
   - Open the .env file and replace the placeholder values with your actual database URL and secret key:
     DATABASE_URL=mysql://your_username:your_password@your_host/your_database
     SECRET_KEY=your_secret_key_here
   IMPORTANT: Never commit your .env file to the repository. It's already in .gitignore to prevent accidental commits.

5. Set up the database:
   - Create a MySQL database
   - The tables will be automatically created when you run the application for the first time

6. Run the application:
   uvicorn app.main:app --reload

The API will be available at `http://localhost:8000`

## API Documentation
FastAPI provides automatic API documentation. Once the application is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- POST /token: Obtain JWT token

### Users
- POST /users/: Create a new user
- GET /users/: List all users
- GET /users/{user_id}: Get a specific user
- GET /users/search/: Search users by name
- POST /users/{user_id}/follow/{target_id}: Follow a user
- POST /users/{user_id}/unfollow/{target_id}: Unfollow a user

### Discussions (Posts)
- POST /discussions/: Create a new discussion
- GET /discussions/: List all discussions
- GET /discussions/{discussion_id}: Get a specific discussion
- PUT /discussions/{discussion_id}: Update a discussion
- DELETE /discussions/{discussion_id}: Delete a discussion
- GET /discussions/hashtag/{hashtag}: Get discussions by hashtag
- POST /discussions/{discussion_id}/like: Like a discussion
- DELETE /discussions/{discussion_id}/like: Unlike a discussion
- POST /discussions/{discussion_id}/view: Increment view count

### Comments
- POST /discussions/{discussion_id}/comments/: Create a comment
- GET /discussions/{discussion_id}/comments/: List comments for a discussion
- POST /comments/{comment_id}/reply: Reply to a comment
- POST /comments/{comment_id}/like: Like a comment
- DELETE /comments/{comment_id}/like: Unlike a comment
- PUT /comments/{comment_id}: Update a comment
- DELETE /comments/{comment_id}: Delete a comment

## Development

### Adding New Features
1. Create new models in `app/models.py`
2. Add corresponding schemas in `app/schemas.py`
3. Implement CRUD operations in `app/crud.py`
4. Add new endpoints in `app/main.py`

### Running Tests

We use pytest for our test suite. To run the tests:

1. Ensure you're in your virtual environment
2. Install test dependencies:
   pip install pytest pytest-fastapi-deps

3. Run the tests:
   pytest

For more verbose output, use:
pytest -v

To run tests with coverage report:
pytest --cov=app --cov-report=term-missing

#### Writing Tests

When adding new features, please include appropriate tests:

1. Create test files in the `tests/` directory
2. Name test files with the prefix `test_`, e.g., `test_users.py`
3. Write test functions prefixed with `test_`
4. Use pytest fixtures for setup and teardown

Example test structure:

# tests/test_users.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

Remember to mock external services and use a separate test database to ensure your tests don't affect your development or production data.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the existing coding style.