import unittest

from app.moderation import ModerationBlocked, enforce_local_policy


class ModerationTests(unittest.TestCase):
    def test_blocks_drug_terms(self):
        with self.assertRaises(ModerationBlocked) as context:
            enforce_local_policy("foto de drogas incautadas")

        self.assertIn("contenido de drogas", context.exception.categories)

    def test_blocks_sexual_terms(self):
        with self.assertRaises(ModerationBlocked) as context:
            enforce_local_policy("comentario con sexo explicito")

        self.assertIn("contenido sexual o adulto", context.exception.categories)

    def test_allows_safe_text(self):
        enforce_local_policy("decoracion neon para una habitacion gamer")


if __name__ == "__main__":
    unittest.main()
