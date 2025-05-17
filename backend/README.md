# Visual DM Backend

## Table of Contents
- [Overview](#overview)
- [Setup](#setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Kubernetes & Helm Deployment](#kubernetes--helm-deployment)

This is the backend API for the Visual_DM project, built with FastAPI and enhanced security features.

## Features

- Modern FastAPI-based REST API 
- JWT-based authentication
- Role-based access control
- Middleware for request logging, rate limiting, and security headers
- Centralized error handling
- Database integration with SQLAlchemy
- Environment-based configuration
- Comprehensive API documentation
- Health monitoring endpoints

## Directory Structure

```
backend/
├── app/
│   ├── api/                # API routes
│   │   ├── v1/             # API version 1
│   │   └── __init__.py     # API router
│   ├── core/               # Core components
│   │   ├── config.py       # App configuration
│   │   ├── dependencies.py # FastAPI dependencies
│   │   ├── errors.py       # Error handling
│   │   ├── logging.py      # Logging configuration
│   │   ├── middleware.py   # Custom middleware
│   │   └── security.py     # Security utilities
│   ├── db/                 # Database components
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   ├── database.py         # Database session
│   └── main.py             # Application entry point
├── migrations/             # Alembic migrations
├── scripts/                # Utility scripts
├── tests/                  # Tests
├── .env                    # Environment variables (not in version control)
├── .env.example            # Example environment variables
└── requirements.txt        # Dependencies
```

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL (or another compatible database)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/visualdm
   SECRET_KEY=your-secret-key
   BACKEND_CORS_ORIGINS=["http://localhost:3000"]
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at http://localhost:8000.
API documentation will be available at http://localhost:8000/docs.

## API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI Schema: `/api/v1/openapi.json`

## Authentication

The API uses JWT tokens for authentication:

1. Obtain a token by sending a POST request to `/api/v1/auth/login` with username and password
2. Include the token in the `Authorization` header for protected endpoints:
   ```
   Authorization: Bearer <your-token>
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection URL | `sqlite:///./app.db` |
| SECRET_KEY | Secret key for JWT encoding | `development_secret_key_change_in_production` |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT token expiration time | `30` |
| BACKEND_CORS_ORIGINS | Allowed CORS origins | `["*"]` |
| RATE_LIMIT_PER_MINUTE | API rate limit per client | `60` |
| LOG_LEVEL | Logging level | `INFO` |
| LOG_FILE | Log file path | `None` (console logging only) |

## Development Guidelines

### Adding a New Endpoint

1. Create a new route file in `/app/api/` or add to an existing one
2. Use dependency injection for database and security
3. Use Pydantic models for request/response validation
4. Include docstrings with detailed descriptions
5. Add appropriate error handling
6. Include the router in `/app/api/__init__.py`

### Adding a Database Model

1. Create a new model in `/app/models/`
2. Make sure it inherits from `Base`