from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class AuthenticationTest(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
        }
        self.user = User.objects.create_user(
            email=self.user_data["email"],
            username=self.user_data["username"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
            password=self.user_data["password"],
        )

    def test_user_creation(self):
        """Test that user is created correctly"""
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.username, self.user_data["username"])
        self.assertTrue(user.check_password(self.user_data["password"]))

    def test_token_login(self):
        """Test token login endpoint"""
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("auth_token", response.data)

    def test_token_login_wrong_password(self):
        """Test token login with wrong password"""
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.user_data["email"], "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_login_wrong_email(self):
        """Test token login with wrong email"""
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": "wrong@example.com", "password": self.user_data["password"]}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
