import pytest
from fastapi import HTTPException
from datetime import datetime
from app.auth import verify_password, get_current_user, create_access_token

async def test_verify_password():
    # Test with correct password
    assert verify_password("test123", "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYqeScNazS")
    # Test with incorrect password
    assert not verify_password("wrong_password", "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYqeScNazS")

async def test_create_access_token(test_user):
    token = create_access_token({"sub": test_user["email"]})
    assert isinstance(token, str)
    assert len(token) > 0

async def test_get_current_user(test_app, test_token, setup_test_db):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = test_app.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

async def test_get_current_user_invalid_token(test_app):
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_app.get("/api/users/me", headers=headers)
    assert response.status_code == 401

async def test_login(test_app, setup_test_db):
    response = test_app.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "test123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

async def test_login_invalid_credentials(test_app, setup_test_db):
    response = test_app.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "wrong_password"}
    )
    assert response.status_code == 401

async def test_register(test_app):
    response = test_app.post(
        "/api/auth/register",
        json={
            "email": "new_user@example.com",
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new_user@example.com"

async def test_register_existing_email(test_app, setup_test_db):
    response = test_app.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "test123",
            "confirm_password": "test123"
        }
    )
    assert response.status_code == 400 