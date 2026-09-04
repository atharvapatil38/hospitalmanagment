import pytest
from tests.conftest import login_user
from app.models import User

def test_login_page_renders(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"CarePlus" in response.data
    assert b"Sign In" in response.data

def test_successful_admin_login(client, init_db):
    response = login_user(client, 'admin@careplus.com', 'Admin@123')
    assert response.status_code == 200
    assert b"Executive Hospital Overview" in response.data or b"Dashboard" in response.data

def test_invalid_password_rejected(client, init_db):
    response = login_user(client, 'admin@careplus.com', 'WrongPassword!')
    assert response.status_code == 200
    assert b"Invalid email address or password" in response.data

def test_logout(client, init_db):
    login_user(client, 'admin@careplus.com', 'Admin@123')
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been securely signed out" in response.data

def test_role_based_access_control(client, init_db):
    # Log in as Receptionist and attempt to access System Settings (Admin only)
    login_user(client, 'reception@careplus.com', 'Reception@123')
    response = client.get('/settings/')
    assert response.status_code in [403, 302]
