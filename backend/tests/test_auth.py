import unittest

from app.auth import decode_access_token, hash_password, verify_password
from app.models import User


class AuthTests(unittest.TestCase):
    def test_hash_password_is_not_plain_text(self):
        hashed = hash_password("super-secret")

        self.assertNotEqual(hashed, "super-secret")
        self.assertTrue(hashed.startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password("super-secret", hashed))
        self.assertFalse(verify_password("wrong", hashed))

    def test_access_token_can_be_decoded(self):
        user = User(id=7, username="akemi", email="a@test.com", password="x")
        token = __import__("app.auth", fromlist=["create_access_token"]).create_access_token(user)
        payload = decode_access_token(token)

        self.assertEqual(payload["sub"], "7")
        self.assertEqual(payload["username"], "akemi")


if __name__ == "__main__":
    unittest.main()
