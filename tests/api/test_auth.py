import pytest
from datetime import timedelta
from unittest.mock import patch
from tests.utils.test_utils import TestUtils, AsyncTestUtils, DBTestUtils
from app.models.user import User
from app.services.auth import AuthService
from app.core.security import create_access_token

@pytest.mark.asyncio
class TestAuthEndpoints:
    @pytest.fixture
    async def auth_service(self):
        return AuthService()

    @pytest.fixture
    def test_user_data(self):
        return {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }

    @pytest.fixture
    async def test_user(self, test_user_data):
        user = DBTestUtils.create_test_model(
            User,
            email=test_user_data["email"],
            hashed_password="hashed_password",
            full_name=test_user_data["full_name"],
            is_active=True
        )
        return user

    async def test_login_success(self, client, test_user, auth_service, mock_db):
        # Mock the database query
        mock_db.query.return_value.filter.return_value.first.return_value = test_user
        
        # Mock password verification
        with patch('app.core.security.verify_password', return_value=True):
            response = await client.post(
                "/auth/login",
                json={
                    "email": test_user.email,
                    "password": "testpassword123"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client, test_user, auth_service, mock_db):
        # Mock the database query
        mock_db.query.return_value.filter.return_value.first.return_value = test_user
        
        # Mock password verification to fail
        with patch('app.core.security.verify_password', return_value=False):
            response = await client.post(
                "/auth/login",
                json={
                    "email": test_user.email,
                    "password": "wrongpassword"
                }
            )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    async def test_login_inactive_user(self, client, test_user, auth_service, mock_db):
        # Set user as inactive
        test_user.is_active = False
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        response = await client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Inactive user"

    async def test_register_success(self, client, test_user_data, auth_service, mock_db):
        # Mock user creation
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Mock email uniqueness check
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = await client.post(
            "/auth/register",
            json=test_user_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "password" not in data

    async def test_register_existing_email(self, client, test_user, test_user_data, auth_service, mock_db):
        # Mock existing user
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        response = await client.post(
            "/auth/register",
            json=test_user_data
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    async def test_refresh_token(self, client, test_user, auth_service, mock_db):
        # Create a valid token
        access_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(minutes=15)
        )
        
        # Mock user retrieval
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        response = await client.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.parametrize("env_vars", [
        {"JWT_SECRET_KEY": "test_key", "JWT_ALGORITHM": "HS256"},
        {"JWT_SECRET_KEY": "another_key", "JWT_ALGORITHM": "HS512"}
    ])
    async def test_token_creation_with_different_configs(self, env_vars, test_user):
        with TestUtils.mock_env(**env_vars):
            token = create_access_token(
                data={"sub": test_user.email},
                expires_delta=timedelta(minutes=15)
            )
            assert token is not None

    async def test_logout(self, client, test_user, auth_service):
        # Create a valid token
        access_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(minutes=15)
        )

        response = await client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out" 