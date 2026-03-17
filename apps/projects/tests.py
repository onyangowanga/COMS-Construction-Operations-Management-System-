from django.test import TestCase

from apps.authentication.models import Organization
from apps.common.services import generate_project_code


class ProjectCodeGenerationTests(TestCase):
	def test_generate_project_code_increments_per_organization_and_year(self):
		organization = Organization.objects.create(name='BuildCo')

		code1, sequence1, year1 = generate_project_code(organization, year=2026)
		self.assertEqual(code1, 'PRJ-2026-001')
		self.assertEqual(sequence1, 1)
		self.assertEqual(year1, 2026)

		from apps.projects.models import Project

		Project.objects.create(
			organization=organization,
			name='Project Alpha',
			code=code1,
			year=year1,
			sequence=sequence1,
		)

		code2, sequence2, year2 = generate_project_code(organization, year=2026)
		self.assertEqual(code2, 'PRJ-2026-002')
		self.assertEqual(sequence2, 2)
		self.assertEqual(year2, 2026)
