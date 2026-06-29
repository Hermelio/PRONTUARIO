from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.access_control.models import AccessProfile
from apps.assessments.models import AssessmentField, AssessmentMetric, AssessmentTemplate, ClinicalAssessment
from apps.attendance.models import AttendanceRecord
from apps.finance.models import FinancialEntry, MonthlyClosing
from apps.incidents.models import Incident
from apps.medical_records.models import ClinicalEvolution
from apps.patient_documents.models import PatientDocument
from apps.patients.models import Patient
from apps.professionals.models import Professional
from apps.scheduling.models import Appointment


class Command(BaseCommand):
    help = "Cria um paciente demo com dados clinicos, agenda, check-in, avaliacoes, documentos e financeiro."

    def handle(self, *args, **options):
        today = timezone.localdate()
        professional = self._professional()
        self._professional_user(professional)
        patient = self._patient(professional)

        self._clear_demo_data(patient, professional, today)
        appointments = self._appointments(patient, professional, today)
        self._attendance(appointments["today"])
        self._evolutions(patient, professional, appointments, today)
        self._assessments(patient, professional, today)
        self._incidents(patient, professional, appointments, today)
        self._documents(patient, professional, today)
        self._finance(patient, professional, appointments, today)

        self.stdout.write(self.style.SUCCESS("Paciente demo pronto para testes."))
        self.stdout.write(f"Paciente: {patient.full_name} (id={patient.pk}, CPF={patient.cpf})")
        self.stdout.write(f"Profissional: {professional.full_name}")
        self.stdout.write("Login profissional: profissional_teste / Teste@12345")
        self.stdout.write(f"Ficha: /pacientes/{patient.pk}/")
        self.stdout.write(f"Prontuario: /prontuario/pacientes/{patient.pk}/")
        self.stdout.write(f"Indicadores: /indicadores/pacientes/{patient.pk}/")

    def _professional(self):
        professional, _ = Professional.objects.update_or_create(
            cpf="999.000.000-01",
            defaults={
                "full_name": "Profissional Teste",
                "rg": "44.555.666-7",
                "birth_date": "1988-05-12",
                "sex": Professional.Sex.FEMALE,
                "phone": "(11) 97777-1000",
                "email": "profissional.teste@prontuario.demo",
                "zip_code": "01310-100",
                "street": "Avenida Paulista",
                "number": "1000",
                "complement": "Conjunto 1204",
                "neighborhood": "Bela Vista",
                "city": "Sao Paulo",
                "state": "SP",
                "professional_council": "CREFITO",
                "council_number": "123456-F",
                "council_state": "SP",
                "primary_specialty": "Fisioterapia domiciliar",
                "secondary_specialties": "Gerontologia, Ortopedia, Reabilitacao cardiorrespiratoria",
                "hired_at": "2024-03-01",
                "status": Professional.Status.ACTIVE,
            },
        )
        return professional

    def _professional_user(self, professional):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username="profissional_teste",
            defaults={
                "first_name": "Profissional",
                "last_name": "Teste",
                "email": "profissional.teste@prontuario.demo",
                "is_staff": True,
            },
        )
        if created or not user.check_password("Teste@12345"):
            user.set_password("Teste@12345")
        user.is_active = True
        user.is_staff = True
        user.email = "profissional.teste@prontuario.demo"
        user.save()

        profile, _ = AccessProfile.objects.get_or_create(user=user)
        AccessProfile.objects.filter(professional=professional).exclude(pk=profile.pk).update(professional=None)
        profile.role = AccessProfile.Role.PROFESSIONAL
        profile.professional = professional
        profile.save()
        return user

    def _patient(self, professional):
        patient, _ = Patient.objects.update_or_create(
            cpf="123.123.123-99",
            defaults={
                "full_name": "Maria Helena dos Santos",
                "birth_date": "1948-09-20",
                "sex": Patient.Sex.FEMALE,
                "phone": "(11) 98888-0101",
                "email": "maria.helena@familia.demo",
                "status": Patient.Status.ACTIVE,
                "zip_code": "01415-001",
                "street": "Rua Haddock Lobo",
                "number": "595",
                "complement": "Apto 82",
                "neighborhood": "Cerqueira Cesar",
                "city": "Sao Paulo",
                "state": "SP",
                "latitude": Decimal("-23.560978"),
                "longitude": Decimal("-46.663095"),
                "primary_diagnosis": "Reabilitacao pos-fratura de femur direito",
                "secondary_diagnoses": "Sarcopenia leve; risco aumentado de quedas",
                "comorbidities": "Hipertensao arterial sistemica; diabetes mellitus tipo 2 controlado",
                "allergies": "Dipirona",
                "current_medications": "Losartana 50mg 12/12h; Metformina 850mg 12/12h; Vitamina D semanal",
                "clinical_notes": (
                    "Paciente em acompanhamento domiciliar, deambula com andador e necessita supervisao "
                    "para transferencias. Familia orientada quanto a prevencao de quedas."
                ),
                "responsible_name": "Carolina Santos Almeida",
                "responsible_relationship": "Filha",
                "responsible_phone": "(11) 97777-0202",
                "responsible_email": "carolina.santos@familia.demo",
                "assigned_professional": professional,
                "referring_professional_name": "Dr. Roberto Lima",
                "referring_professional_specialty": "Ortopedia",
                "referring_professional_council": "CRM-SP 123456",
                "referring_professional_phone": "(11) 3333-1212",
                "referring_professional_email": "roberto.lima@clinica.demo",
            },
        )
        return patient

    def _clear_demo_data(self, patient, professional, today):
        FinancialEntry.objects.filter(patient=patient).delete()
        MonthlyClosing.objects.filter(professional=professional, start_date__year=today.year, start_date__month=today.month).delete()
        ClinicalEvolution.objects.filter(patient=patient).delete()
        ClinicalAssessment.objects.filter(patient=patient).delete()
        Incident.objects.filter(patient=patient).delete()
        PatientDocument.objects.filter(patient=patient).delete()
        Appointment.objects.filter(patient=patient).delete()

    def _aware(self, day, hour, minute=0):
        return timezone.make_aware(datetime.combine(day, time(hour, minute)), timezone.get_current_timezone())

    def _appointments(self, patient, professional, today):
        appointment_data = {
            "last_week": {
                "date": today - timedelta(days=7),
                "starts_at": time(10, 0),
                "ends_at": time(11, 0),
                "status": Appointment.Status.COMPLETED,
                "notes": "Sessao de fortalecimento e treino de marcha realizada conforme plano.",
            },
            "today": {
                "date": today,
                "starts_at": time(14, 0),
                "ends_at": time(15, 0),
                "status": Appointment.Status.COMPLETED,
                "notes": "Atendimento com check-in por geolocalizacao e evolucao vinculada.",
            },
            "next": {
                "date": today + timedelta(days=2),
                "starts_at": time(9, 0),
                "ends_at": time(10, 0),
                "status": Appointment.Status.CONFIRMED,
                "notes": "Proximo atendimento: reavaliar dor, equilibrio e tolerancia ao treino.",
            },
            "recurring": {
                "date": today + timedelta(days=5),
                "starts_at": time(15, 30),
                "ends_at": time(16, 30),
                "status": Appointment.Status.SCHEDULED,
                "notes": "Plano recorrente: fisioterapia 3 vezes por semana.",
                "recurrence_frequency": Appointment.RecurrenceFrequency.WEEKLY,
                "recurrence_weekdays": "0,2,4",
                "recurrence_until": today + timedelta(days=60),
            },
        }
        appointments = {}
        for key, data in appointment_data.items():
            defaults = {
                "appointment_type": Appointment.AppointmentType.PHYSIOTHERAPY,
                "recurrence_frequency": data.get("recurrence_frequency", Appointment.RecurrenceFrequency.NONE),
                "recurrence_interval": 1,
                "recurrence_weekdays": data.get("recurrence_weekdays", ""),
                "recurrence_until": data.get("recurrence_until"),
                "notes": data["notes"],
                "status": data["status"],
            }
            appointments[key] = Appointment.objects.create(
                patient=patient,
                professional=professional,
                date=data["date"],
                starts_at=data["starts_at"],
                ends_at=data["ends_at"],
                **defaults,
            )
        return appointments

    def _attendance(self, appointment):
        record = AttendanceRecord(appointment=appointment)
        check_in_at = self._aware(appointment.date, 14, 3)
        check_out_at = self._aware(appointment.date, 15, 5)
        record.register_check_in("-23.560950", "-46.663070", radius_meters=100, checked_at=check_in_at)
        record.register_check_out("-23.560940", "-46.663060", checked_at=check_out_at)
        record.notes = "Check-in autorizado dentro do raio configurado de 100 metros."
        record.save()

    def _evolutions(self, patient, professional, appointments, today):
        ClinicalEvolution.objects.create(
            patient=patient,
            professional=professional,
            appointment=appointments["last_week"],
            date=today - timedelta(days=7),
            time=time(10, 55),
            service_description=(
                "Paciente realizou treino de marcha com andador por 12 minutos, com duas pausas curtas. "
                "Relatou dor moderada em quadril direito ao final da atividade."
            ),
            procedures_performed="Mobilizacao ativa assistida; treino de sentar-levantar; orientacao familiar.",
            conduct="Manter frequencia de 3 atendimentos semanais e reforcar exercicios domiciliares supervisionados.",
            notes="Sem sinais de instabilidade hemodinamica.",
        )
        ClinicalEvolution.objects.create(
            patient=patient,
            professional=professional,
            appointment=appointments["today"],
            date=today,
            time=time(15, 5),
            service_description=(
                "Boa adesao ao atendimento. Evoluiu com maior seguranca nas transferencias e menor dor "
                "durante treino funcional no corredor do apartamento."
            ),
            procedures_performed="Fortalecimento de MMII; treino de equilibrio estatico; marcha assistida; alongamentos leves.",
            conduct="Progredir distancia de marcha no proximo atendimento e repetir escala de dor em 48 horas.",
            notes="Familia orientada a manter tapetes removidos e iluminacao noturna.",
        )

    def _assessment_template(self):
        template, _ = AssessmentTemplate.objects.update_or_create(
            name="Avaliacao Gerontologica Funcional",
            defaults={
                "specialty": AssessmentTemplate.Specialty.GERONTOLOGICAL,
                "description": "Modelo de acompanhamento funcional para paciente domiciliar.",
                "is_active": True,
            },
        )
        fields = [
            ("Dor", AssessmentField.FieldType.SCALE, "0-10", 1),
            ("Forca muscular", AssessmentField.FieldType.SCALE, "MRC", 2),
            ("Mobilidade", AssessmentField.FieldType.SCALE, "0-100", 3),
            ("Equilibrio", AssessmentField.FieldType.SCALE, "0-56", 4),
        ]
        result = {}
        for label, field_type, unit, order in fields:
            field, _ = AssessmentField.objects.update_or_create(
                template=template,
                label=label,
                defaults={
                    "field_type": field_type,
                    "unit": unit,
                    "is_required": True,
                    "order": order,
                },
            )
            result[label] = field
        return template, result

    def _assessments(self, patient, professional, today):
        template, fields = self._assessment_template()
        assessment_data = [
            (today - timedelta(days=60), "Avaliacao inicial com dor importante e mobilidade reduzida.", {
                "Dor": (Decimal("8.00"), "0-10", False),
                "Forca muscular": (Decimal("3.00"), "MRC", True),
                "Mobilidade": (Decimal("42.00"), "0-100", True),
                "Equilibrio": (Decimal("28.00"), "0-56", True),
            }),
            (today - timedelta(days=30), "Reavaliacao com melhora parcial apos adesao ao plano.", {
                "Dor": (Decimal("5.00"), "0-10", False),
                "Forca muscular": (Decimal("4.00"), "MRC", True),
                "Mobilidade": (Decimal("58.00"), "0-100", True),
                "Equilibrio": (Decimal("36.00"), "0-56", True),
            }),
            (today, "Reavaliacao atual demonstra melhora funcional sustentada.", {
                "Dor": (Decimal("3.00"), "0-10", False),
                "Forca muscular": (Decimal("4.50"), "MRC", True),
                "Mobilidade": (Decimal("71.00"), "0-100", True),
                "Equilibrio": (Decimal("44.00"), "0-56", True),
            }),
        ]
        for day, summary, metrics in assessment_data:
            assessment = ClinicalAssessment.objects.create(
                patient=patient,
                professional=professional,
                template=template,
                performed_at=self._aware(day, 11, 30),
                summary=summary,
            )
            for name, (value, unit, higher_is_better) in metrics.items():
                AssessmentMetric.objects.create(
                    assessment=assessment,
                    field=fields[name],
                    name=name,
                    numeric_value=value,
                    unit=unit,
                    higher_is_better=higher_is_better,
                )

    def _incidents(self, patient, professional, appointments, today):
        Incident.objects.create(
            patient=patient,
            professional=professional,
            appointment=appointments["last_week"],
            date=today - timedelta(days=7),
            time=time(10, 42),
            description="Paciente relatou tontura leve apos treino de sentar-levantar.",
            severity=Incident.Classification.MILD,
            classification=Incident.Classification.MILD,
            conduct_performed="Atividade pausada, sinais vitais checados e hidratacao orientada. Sintoma cessou em poucos minutos.",
        )

    def _documents(self, patient, professional, today):
        document = PatientDocument(
            patient=patient,
            uploaded_by=professional,
            title="Laudo ortopedico pos-operativo",
            document_type=PatientDocument.DocumentType.MEDICAL_REPORT,
            document_date=today - timedelta(days=75),
            description="Documento demo para validar anexos vinculados ao paciente.",
        )
        document.file.save(
            "laudo-ortopedico-demo.txt",
            ContentFile("Laudo demo: fratura de femur direito em reabilitacao domiciliar."),
            save=True,
        )
        prescription = PatientDocument(
            patient=patient,
            uploaded_by=professional,
            title="Receita medica atualizada",
            document_type=PatientDocument.DocumentType.PRESCRIPTION,
            document_date=today - timedelta(days=15),
            description="Receita demo para testar listagem de documentos.",
        )
        prescription.file.save(
            "receita-demo.txt",
            ContentFile("Receita demo: medicacoes de uso continuo registradas no prontuario."),
            save=True,
        )

    def _finance(self, patient, professional, appointments, today):
        FinancialEntry.objects.create(
            appointment=appointments["last_week"],
            patient=patient,
            professional=professional,
            reference_date=today - timedelta(days=7),
            appointment_quantity=1,
            appointment_value=Decimal("180.00"),
            payer_type=FinancialEntry.PayerType.PRIVATE,
            company_percentage=Decimal("30.00"),
            professional_percentage=Decimal("70.00"),
            status=FinancialEntry.Status.RECEIVED,
            notes="Atendimento particular recebido.",
        )
        FinancialEntry.objects.create(
            appointment=appointments["today"],
            patient=patient,
            professional=professional,
            reference_date=today,
            appointment_quantity=1,
            appointment_value=Decimal("180.00"),
            payer_type=FinancialEntry.PayerType.INSURANCE,
            insurance_name="Convenio Demo Vida",
            company_percentage=Decimal("35.00"),
            professional_percentage=Decimal("65.00"),
            status=FinancialEntry.Status.PENDING,
            notes="Lancamento pendente para testar valores a receber.",
        )
        start_date = today.replace(day=1)
        next_month = (start_date + timedelta(days=32)).replace(day=1)
        MonthlyClosing.objects.create(
            start_date=start_date,
            end_date=next_month - timedelta(days=1),
            professional=professional,
        )
