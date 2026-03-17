from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.authentication.models import Organization
from apps.projects.models import Project
from apps.subcontracts.models import SubcontractAgreement, Subcontractor
from apps.subcontracts.services import SubcontractService


class SubcontractCodeGenerationTests(TestCase):
    def test_create_subcontract_and_claim_assign_scope_metadata(self):
        user_model = get_user_model()
        organization = Organization.objects.create(name='Subcontract Org')
        user = user_model.objects.create_user(username='subcontract-user', password='secret', organization=organization)
        project = Project.objects.create(
            organization=organization,
            name='Tower Build',
            code='PRJ-2026-005',
            year=2026,
            sequence=5,
        )
        subcontractor = Subcontractor.objects.create(
            organization=organization,
            name='Electrical Works Ltd',
            contact_person='Jane Doe',
            phone='+254711111111',
            email='jane@example.com',
            address='Nairobi',
            created_by=user,
        )

        subcontract = SubcontractService.create_subcontract(
            project=project,
            subcontractor=subcontractor,
            contract_reference='',
            scope_of_work='Electrical installation',
            contract_value=Decimal('50000.00'),
            start_date=date(2026, 3, 1),
            end_date=date(2026, 4, 1),
            created_by=user,
        )
        subcontract.status = SubcontractAgreement.Status.ACTIVE
        subcontract.save(update_fields=['status', 'updated_at'])

        claim = SubcontractService.submit_claim(
            subcontract=subcontract,
            claim_number='',
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 15),
            claimed_amount=Decimal('10000.00'),
            submitted_by=user,
        )

        self.assertEqual(subcontract.organization, organization)
        self.assertEqual(subcontract.year, 2026)
        self.assertEqual(subcontract.sequence, 1)
        self.assertEqual(subcontract.contract_reference, 'SC-2026-001')
        self.assertEqual(claim.project, project)
        self.assertEqual(claim.sequence, 1)
        self.assertEqual(claim.claim_number, 'CL-PRJ-2026-005-001')