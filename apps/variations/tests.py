from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.authentication.models import Organization
from apps.projects.models import Project
from apps.variations.services import VariationService


class VariationCodeGenerationTests(TestCase):
	def test_create_variation_sets_project_scoped_sequence(self):
		user_model = get_user_model()
		organization = Organization.objects.create(name='Variation Org')
		user = user_model.objects.create_user(username='variation-user', password='secret', organization=organization)
		project = Project.objects.create(
			organization=organization,
			name='Main Project',
			code='PRJ-2026-010',
			year=2026,
			sequence=10,
		)

		variation1 = VariationService.create_variation(
			project_id=str(project.id),
			title='Extra beam work',
			description='Add extra beam reinforcement',
			estimated_value=Decimal('1000.00'),
			instruction_date='2026-03-01',
			created_by=user,
		)
		variation2 = VariationService.create_variation(
			project_id=str(project.id),
			title='Additional plaster',
			description='Increase plaster scope',
			estimated_value=Decimal('2000.00'),
			instruction_date='2026-03-02',
			created_by=user,
		)

		self.assertEqual(variation1.reference_number, 'VO-PRJ-2026-010-001')
		self.assertEqual(variation1.sequence, 1)
		self.assertEqual(variation2.reference_number, 'VO-PRJ-2026-010-002')
		self.assertEqual(variation2.sequence, 2)

	def test_superuser_can_override_reference_number(self):
		user_model = get_user_model()
		organization = Organization.objects.create(name='Variation Admin Org')
		admin_user = user_model.objects.create_user(
			username='variation-admin',
			password='secret',
			organization=organization,
			is_superuser=True,
			is_staff=True,
		)
		project = Project.objects.create(
			organization=organization,
			name='Admin Project',
			code='PRJ-2026-011',
			year=2026,
			sequence=11,
		)

		variation = VariationService.create_variation(
			project_id=str(project.id),
			reference_number='VO-MANUAL-999',
			title='Manual reference variation',
			description='Admin manually set code',
			estimated_value=Decimal('3000.00'),
			instruction_date='2026-03-03',
			created_by=admin_user,
		)

		self.assertEqual(variation.reference_number, 'VO-MANUAL-999')
		self.assertEqual(variation.sequence, 1)
