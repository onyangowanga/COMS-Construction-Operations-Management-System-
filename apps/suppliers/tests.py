from django.test import TestCase

from apps.authentication.models import Organization
from apps.common.services import generate_lpo_number
from apps.projects.models import Project
from apps.suppliers.models import LocalPurchaseOrder, Supplier


class LpoCodeGenerationTests(TestCase):
	def test_generate_lpo_number_increments_per_project(self):
		organization = Organization.objects.create(name='Supplier Org')
		project = Project.objects.create(
			organization=organization,
			name='Procurement Project',
			code='PRJ-2026-001',
			year=2026,
			sequence=1,
		)
		supplier = Supplier.objects.create(
			organization=organization,
			name='Concrete Supply Ltd',
			phone='+254700000000',
		)

		number1, sequence1, _ = generate_lpo_number(project)
		LocalPurchaseOrder.objects.create(
			project=project,
			supplier=supplier,
			lpo_number=number1,
			sequence=sequence1,
			issue_date='2026-03-01',
			total_amount='1000.00',
		)

		number2, sequence2, _ = generate_lpo_number(project)
		self.assertEqual(number1, 'LPO-PRJ-2026-001-001')
		self.assertEqual(number2, 'LPO-PRJ-2026-001-002')
		self.assertEqual(sequence2, 2)
