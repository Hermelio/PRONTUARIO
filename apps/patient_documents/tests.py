from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.patients.models import Patient

from .models import PatientDocument


class PatientDocumentModelTests(TestCase):
    def test_patient_document_string_representation(self):
        patient = Patient.objects.create(full_name="Paciente Documento", cpf="902.000.000-00")
        document = PatientDocument.objects.create(
            patient=patient,
            title="Hemograma",
            document_type=PatientDocument.DocumentType.LAB_EXAM,
            file=SimpleUploadedFile("hemograma.pdf", b"fake-pdf", content_type="application/pdf"),
        )

        self.assertEqual(str(document), "Paciente Documento - Hemograma")
