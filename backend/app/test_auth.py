import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.schemas.auth import UserCreate, UserLogin
from app.services.auth_service import register_user, authenticate_user, get_user_by_username
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.api.routes.auth import register, login, read_users_me, get_current_user
from fastapi import HTTPException


class TestAuthServicesAndSecurity(unittest.TestCase):

    def test_security_hash_and_verify(self):
        password = "mysecretpassword"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrongpassword", hashed))

    def test_jwt_token_create_and_decode(self):
        data = {"sub": "testuser"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded.get("sub"), "testuser")

    @patch("app.services.auth_service.users_collection")
    def test_register_user_service_success(self, mock_users_coll):
        mock_users_coll.find_one.return_value = None
        mock_users_coll.insert_one.return_value = MagicMock(inserted_id="507f1f77bcf86cd799439011")

        user_in = UserCreate(username="newuser", email="newuser@example.com", password="password123")
        res = register_user(user_in)

        self.assertEqual(res["username"], "newuser")
        self.assertEqual(res["email"], "newuser@example.com")
        self.assertEqual(res["id"], "507f1f77bcf86cd799439011")

    @patch("app.services.auth_service.users_collection")
    def test_register_user_service_duplicate(self, mock_users_coll):
        mock_users_coll.find_one.return_value = {"username": "existinguser", "email": "existing@example.com"}

        user_in = UserCreate(username="existinguser", email="new@example.com", password="password123")
        with self.assertRaises(ValueError):
            register_user(user_in)

    @patch("app.services.auth_service.users_collection")
    def test_authenticate_user_success(self, mock_users_coll):
        hashed_pwd = hash_password("secret123")
        mock_users_coll.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "username": "validuser",
            "email": "valid@example.com",
            "hashed_password": hashed_pwd,
        }

        user_in = UserLogin(username="validuser", password="secret123")
        user = authenticate_user(user_in)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "validuser")

    @patch("app.services.auth_service.users_collection")
    def test_authenticate_user_invalid(self, mock_users_coll):
        hashed_pwd = hash_password("secret123")
        mock_users_coll.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "username": "validuser",
            "email": "valid@example.com",
            "hashed_password": hashed_pwd,
        }

        user_in = UserLogin(username="validuser", password="wrongpassword")
        user = authenticate_user(user_in)
        self.assertIsNone(user)

    @patch("app.services.auth_service.users_collection")
    def test_route_login_endpoint(self, mock_users_coll):
        hashed_pwd = hash_password("secret123")
        mock_users_coll.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "username": "validuser",
            "email": "valid@example.com",
            "hashed_password": hashed_pwd,
        }

        user_in = UserLogin(username="validuser", password="secret123")
        token_res = login(user_in)
        self.assertIn("access_token", token_res)
        self.assertEqual(token_res["token_type"], "bearer")

    @patch("app.services.auth_service.users_collection")
    def test_get_current_user_dependency(self, mock_users_coll):
        mock_users_coll.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "username": "validuser",
            "email": "valid@example.com",
        }
        token = create_access_token({"sub": "validuser"})
        user = get_current_user(token)
        self.assertEqual(user["username"], "validuser")

    def test_get_current_user_no_token(self):
        with self.assertRaises(HTTPException) as cm:
            get_current_user(None)
        self.assertEqual(cm.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
