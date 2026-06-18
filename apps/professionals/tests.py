from django.test import TestCase

from .models import Professional


class ProfessionalModelTests(TestCase):
    def test_professional_string_representation(self):
        professional = Professional.objects.create(
            full_name="Ana Paula Souza",
            cpf="123.456.789-00",
        )

        self.assertEqual(str(professional), "Ana Paula Souza")
