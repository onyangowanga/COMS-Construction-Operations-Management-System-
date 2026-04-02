"""
Management command to populate database with realistic demo data for client pitches.
Usage: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Max
from decimal import Decimal
from datetime import datetime, timedelta
import random

from apps.authentication.models import Organization
from apps.projects.models import Project, ProjectStage
from apps.subcontracts.models import Subcontractor, SubcontractAgreement, SubcontractClaim
from apps.suppliers.models import Supplier, LocalPurchaseOrder
from apps.clients.models import ClientPayment

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with demo data for client pitches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing demo data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting demo data seeding...'))

        # Get or create organization
        org = self._get_or_create_organization()

        # Get admin user
        admin_user = self._get_admin_user()

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing demo data...'))
            self._clear_demo_data(org)

        # Seed data
        self.stdout.write('Creating projects...')
        projects = self._create_projects(org)

        self.stdout.write('Creating suppliers...')
        suppliers = self._create_suppliers(org)

        self.stdout.write('Creating subcontractors...')
        subcontractors = self._create_subcontractors(org, admin_user)

        self.stdout.write('Creating LPOs...')
        self._create_lpos(suppliers, projects)

        self.stdout.write('Creating subcontracts...')
        self._create_subcontracts(subcontractors, projects, admin_user)

        self.stdout.write('Creating client payments...')
        self._create_client_payments(projects)

        self.stdout.write('Creating project stages...')
        self._create_project_stages(projects)

        self.stdout.write(self.style.SUCCESS(f'\n✅ Demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'   • {len(projects)} Projects'))
        self.stdout.write(self.style.SUCCESS(f'   • {len(suppliers)} Suppliers'))
        self.stdout.write(self.style.SUCCESS(f'   • {len(subcontractors)} Subcontractors'))

    def _get_or_create_organization(self):
        """Get or create default organization"""
        org, created = Organization.objects.get_or_create(
            name='Premier Construction Ltd',
            defaults={
                'org_type': 'contractor',
                'city': 'Nairobi',
                'country': 'Kenya',
                'default_currency': 'KES',
                'fiscal_year_start': 'January 1',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created organization: {org.name}'))
        else:
            self.stdout.write(f'Using existing organization: {org.name}')
        return org

    def _get_admin_user(self):
        """Get admin user"""
        try:
            return User.objects.filter(is_superuser=True).first() or User.objects.first()
        except:
            return None

    def _clear_demo_data(self, org):
        """Clear existing demo data"""
        Project.objects.filter(organization=org).delete()
        Supplier.objects.filter(organization=org).delete()
        Subcontractor.objects.filter(organization=org).delete()

    def _create_projects(self, org):
        """Create 5 demo projects"""
        projects_data = [
            {
                'name': 'Riverside Corporate Towers',
                'code': 'PRJ-2026-001',
                'year': 2026,
                'sequence': 1,
                'client_name': 'Riverside Development Corporation',
                'location': 'Westlands, Nairobi',
                'project_type': Project.ProjectType.NEW_CONSTRUCTION,
                'contract_type': Project.ContractType.FULL_CONTRACT,
                'project_value': Decimal('450000000.00'),
                'start_date': datetime(2026, 1, 15).date(),
                'end_date': datetime(2027, 6, 30).date(),
                'status': Project.Status.IMPLEMENTATION,
                'description': 'Modern 12-story corporate office complex with underground parking, featuring eco-friendly design and smart building technology.',
            },
            {
                'name': 'Green Valley Residential Estate',
                'code': 'PRJ-2026-002',
                'year': 2026,
                'sequence': 2,
                'client_name': 'Green Valley Developers',
                'location': 'Karen, Nairobi',
                'project_type': Project.ProjectType.NEW_CONSTRUCTION,
                'contract_type': Project.ContractType.FULL_CONTRACT,
                'project_value': Decimal('280000000.00'),
                'start_date': datetime(2026, 2, 1).date(),
                'end_date': datetime(2027, 3, 31).date(),
                'status': Project.Status.IMPLEMENTATION,
                'description': '45-unit luxury residential estate with clubhouse, swimming pool, and landscaped gardens.',
            },
            {
                'name': 'City Mall Renovation',
                'code': 'PRJ-2026-003',
                'year': 2026,
                'sequence': 3,
                'client_name': 'Metro Retail Properties',
                'location': 'CBD, Nairobi',
                'project_type': Project.ProjectType.RENOVATION,
                'contract_type': Project.ContractType.LABOUR_ONLY,
                'project_value': Decimal('85000000.00'),
                'start_date': datetime(2025, 11, 1).date(),
                'end_date': datetime(2026, 5, 31).date(),
                'status': Project.Status.IMPLEMENTATION,
                'description': 'Complete renovation of 4-story shopping mall including facade upgrade, interior remodeling, and MEP systems upgrade.',
            },
            {
                'name': 'Industrial Park Warehouse Complex',
                'code': 'PRJ-2025-015',
                'year': 2025,
                'sequence': 15,
                'client_name': 'Logistics Hub Africa',
                'location': 'Athi River',
                'project_type': Project.ProjectType.NEW_CONSTRUCTION,
                'contract_type': Project.ContractType.FULL_CONTRACT,
                'project_value': Decimal('320000000.00'),
                'start_date': datetime(2025, 7, 1).date(),
                'end_date': datetime(2026, 8, 31).date(),
                'status': Project.Status.COMPLETED,
                'description': '5 warehouse units with modern loading facilities, office blocks, and security infrastructure.',
            },
            {
                'name': 'University Science Complex',
                'code': 'PRJ-2026-004',
                'year': 2026,
                'sequence': 4,
                'client_name': 'National University of Kenya',
                'location': 'Kikuyu, Kiambu',
                'project_type': Project.ProjectType.NEW_CONSTRUCTION,
                'contract_type': Project.ContractType.FULL_CONTRACT,
                'project_value': Decimal('550000000.00'),
                'start_date': datetime(2026, 3, 1).date(),
                'end_date': datetime(2027, 12, 31).date(),
                'status': Project.Status.APPROVAL,
                'description': 'State-of-the-art science and technology complex with laboratories, lecture halls, and research facilities.',
            },
        ]

        projects = []
        for data in projects_data:
            project = Project.objects.create(organization=org, **data)
            projects.append(project)
            self.stdout.write(f'  ✓ Created project: {project.code} - {project.name}')

        return projects

    def _create_suppliers(self, org):
        """Create suppliers"""
        suppliers_data = [
            {
                'name': 'BuildMart Suppliers Ltd',
                'phone': '+254722123456',
                'email': 'sales@buildmart.co.ke',
                'address': 'Industrial Area, Nairobi',
                'tax_pin': 'P051234567A',
                'is_active': True,
            },
            {
                'name': 'Kenya Cement Distributors',
                'phone': '+254733234567',
                'email': 'orders@kenyacement.com',
                'address': 'Mombasa Road, Nairobi',
                'tax_pin': 'P051234568B',
                'is_active': True,
            },
            {
                'name': 'Prime Steel & Hardware',
                'phone': '+254711345678',
                'email': 'info@primesteel.co.ke',
                'address': 'Ruaraka, Nairobi',
                'tax_pin': 'P051234569C',
                'is_active': True,
            },
            {
                'name': 'ElectroPro Solutions',
                'phone': '+254720456789',
                'email': 'sales@electropro.com',
                'address': 'Westlands, Nairobi',
                'tax_pin': 'P051234570D',
                'is_active': True,
            },
            {
                'name': 'Timber & Finishes Co.',
                'phone': '+254734567890',
                'email': 'orders@timberfinishes.co.ke',
                'address': 'Thika Road, Nairobi',
                'tax_pin': 'P051234571E',
                'is_active': True,
            },
        ]

        suppliers = []
        for data in suppliers_data:
            supplier = Supplier.objects.create(organization=org, **data)
            suppliers.append(supplier)
            self.stdout.write(f'  ✓ Created supplier: {supplier.name}')

        return suppliers

    def _create_subcontractors(self, org, admin_user):
        """Create subcontractors"""
        subcontractors_data = [
            {
                'name': 'Excel Electrical Contractors',
                'company_registration': 'C.123456',
                'tax_number': 'P051234580A',
                'contact_person': 'John Kamau',
                'phone': '+254722567890',
                'email': 'contracts@excelelectrical.co.ke',
                'address': 'Industrial Area, Nairobi',
                'specialization': 'Electrical Works',
                'is_active': True,
            },
            {
                'name': 'Premium Plumbing Services',
                'company_registration': 'C.123457',
                'tax_number': 'P051234581B',
                'contact_person': 'Mary Wanjiku',
                'phone': '+254733678901',
                'email': 'info@premiumplumbing.com',
                'address': 'Westlands, Nairobi',
                'specialization': 'Plumbing & Drainage',
                'is_active': True,
            },
            {
                'name': 'Skyline Steel Fabricators',
                'company_registration': 'C.123458',
                'tax_number': 'P051234582C',
                'contact_person': 'David Omondi',
                'phone': '+254711789012',
                'email': 'contracts@skylinesteel.co.ke',
                'address': 'Athi River',
                'specialization': 'Steel Fabrication & Erection',
                'is_active': True,
            },
            {
                'name': 'Interior Finishing Experts',
                'company_registration': 'C.123459',
                'tax_number': 'P051234583D',
                'contact_person': 'Sarah Njeri',
                'phone': '+254720890123',
                'email': 'projects@interiorexperts.com',
                'address': 'Karen, Nairobi',
                'specialization': 'Interior Finishes & Joinery',
                'is_active': True,
            },
            {
                'name': 'Foundation & Ground Works Ltd',
                'company_registration': 'C.123460',
                'tax_number': 'P051234584E',
                'contact_person': 'Peter Mwangi',
                'phone': '+254734901234',
                'email': 'info@foundationworks.co.ke',
                'address': 'Thika Road, Nairobi',
                'specialization': 'Earthworks & Foundation',
                'is_active': True,
            },
        ]

        subcontractors = []
        for data in subcontractors_data:
            subcontractor = Subcontractor.objects.create(
                organization=org,
                created_by=admin_user,
                **data
            )
            subcontractors.append(subcontractor)
            self.stdout.write(f'  ✓ Created subcontractor: {subcontractor.name}')

        return subcontractors

    def _create_lpos(self, suppliers, projects):
        """Create Local Purchase Orders"""
        active_projects = [p for p in projects if p.status == Project.Status.IMPLEMENTATION]

        lpo_sequence = 1
        for project in active_projects[:3]:  # Create LPOs for first 3 active projects
            for i in range(random.randint(2, 4)):
                supplier = random.choice(suppliers)
                lpo = LocalPurchaseOrder.objects.create(
                    supplier=supplier,
                    project=project,
                    lpo_number=f'LPO-{project.code}-{lpo_sequence:03d}',
                    sequence=lpo_sequence,
                    issue_date=project.start_date + timedelta(days=random.randint(10, 90)),
                    total_amount=Decimal(random.randint(50000, 500000)),
                    status=random.choice([
                        LocalPurchaseOrder.Status.APPROVED,
                        LocalPurchaseOrder.Status.ISSUED,
                        LocalPurchaseOrder.Status.DELIVERED,
                    ]),
                    delivery_deadline=project.start_date + timedelta(days=random.randint(30, 120)),
                    notes=f'Purchase order for {project.name}',
                )
                lpo_sequence += 1
                self.stdout.write(f'  ✓ Created LPO: {lpo.lpo_number}')

    def _create_subcontracts(self, subcontractors, projects, admin_user):
        """Create subcontract agreements"""
        active_projects = [p for p in projects if p.status in [
            Project.Status.IMPLEMENTATION,
            Project.Status.COMPLETED
        ]]

        contract_sequence = 1
        for project in active_projects:
            # Create 2-3 subcontracts per active project
            for i in range(random.randint(2, 3)):
                subcontractor = random.choice(subcontractors)
                contract_value = Decimal(random.randint(5000000, 50000000))

                subcontract = SubcontractAgreement.objects.create(
                    project=project,
                    organization=project.organization,
                    subcontractor=subcontractor,
                    contract_reference=f'SC-{project.year}-{contract_sequence:03d}',
                    year=project.year,
                    sequence=contract_sequence,
                    scope_of_work=f'{subcontractor.specialization} works for {project.name}',
                    contract_value=contract_value,
                    retention_percentage=Decimal('10.00'),
                    start_date=project.start_date + timedelta(days=random.randint(15, 45)),
                    end_date=project.end_date - timedelta(days=random.randint(15, 60)),
                    status=SubcontractAgreement.Status.ACTIVE if project.status == Project.Status.IMPLEMENTATION else SubcontractAgreement.Status.COMPLETED,
                    payment_terms='Net 30 days',
                    vat_applicable=True,
                    created_by=admin_user,
                    activated_at=timezone.now() - timedelta(days=random.randint(30, 180)),
                )
                contract_sequence += 1
                self.stdout.write(f'  ✓ Created subcontract: {subcontract.contract_reference}')

                # Create 1-2 claims for each active subcontract
                if subcontract.status == SubcontractAgreement.Status.ACTIVE:
                    self._create_subcontract_claims(subcontract, admin_user)

    def _create_subcontract_claims(self, subcontract, admin_user):
        """Create claims for a subcontract"""
        claim_count = random.randint(1, 3)
        cumulative = Decimal('0.00')
        next_sequence = (
            SubcontractClaim.objects.filter(project=subcontract.project)
            .aggregate(max_sequence=Max('sequence'))
            .get('max_sequence')
            or 0
        ) + 1

        for i in range(1, claim_count + 1):
            claimed_amount = subcontract.contract_value * Decimal(random.randint(20, 40)) / Decimal('100')
            certified_amount = claimed_amount * Decimal(random.randint(85, 100)) / Decimal('100')
            retention = certified_amount * subcontract.retention_percentage / Decimal('100')

            period_start = subcontract.start_date + timedelta(days=(i-1) * 30)
            period_end = period_start + timedelta(days=30)

            claim = SubcontractClaim.objects.create(
                subcontract=subcontract,
                project=subcontract.project,
                claim_number=f'{subcontract.contract_reference}-C{i:03d}',
                sequence=next_sequence,
                period_start=period_start,
                period_end=period_end,
                claimed_amount=claimed_amount,
                certified_amount=certified_amount,
                retention_amount=retention,
                previous_cumulative_amount=cumulative,
                status=random.choice([
                    SubcontractClaim.Status.SUBMITTED,
                    SubcontractClaim.Status.CERTIFIED,
                    SubcontractClaim.Status.PAID,
                ]),
                description=f'Payment claim #{i} for works executed',
                submitted_by=admin_user,
                certified_by=admin_user if i < claim_count else None,
                created_by=admin_user,
                submitted_date=timezone.now() - timedelta(days=random.randint(5, 20)),
                certified_date=timezone.now() - timedelta(days=random.randint(1, 10)) if i < claim_count else None,
            )
            next_sequence += 1
            cumulative += certified_amount
            self.stdout.write(f'    ✓ Created claim: {claim.claim_number}')

    def _create_client_payments(self, projects):
        """Create client payments"""
        for project in projects:
            if project.status in [Project.Status.IMPLEMENTATION, Project.Status.COMPLETED]:
                # Create 1-3 payments per project
                payment_count = random.randint(1, 3)
                for i in range(payment_count):
                    payment_amount = project.project_value * Decimal(random.randint(15, 35)) / Decimal('100')

                    ClientPayment.objects.create(
                        project=project,
                        amount=payment_amount,
                        payment_date=project.start_date + timedelta(days=random.randint(30, 180)),
                        payment_method=random.choice([
                            ClientPayment.PaymentMethod.BANK_TRANSFER,
                            ClientPayment.PaymentMethod.CHEQUE,
                        ]),
                        reference_number=f'PAY-{project.code}-{i+1:03d}',
                        description=f'Progress payment #{i+1} for {project.name}',
                    )
                    self.stdout.write(f'  ✓ Created client payment for {project.code}')

    def _create_project_stages(self, projects):
        """Create project stages"""
        for project in projects:
            if project.status in [Project.Status.IMPLEMENTATION, Project.Status.COMPLETED]:
                stages_data = [
                    {
                        'name': ProjectStage.StageName.PRELIMINARY,
                        'order': 1,
                        'description': 'Site mobilization, temporary works, and preliminaries',
                        'is_completed': True,
                    },
                    {
                        'name': ProjectStage.StageName.SHELL,
                        'order': 2,
                        'description': 'Foundation, structure, and building shell',
                        'is_completed': project.status == Project.Status.COMPLETED,
                    },
                    {
                        'name': ProjectStage.StageName.FINISHES,
                        'order': 3,
                        'description': 'Interior and exterior finishes',
                        'is_completed': project.status == Project.Status.COMPLETED,
                    },
                    {
                        'name': ProjectStage.StageName.EXTERNAL_WORKS,
                        'order': 4,
                        'description': 'External works, landscaping, and utilities',
                        'is_completed': project.status == Project.Status.COMPLETED,
                    },
                ]

                for stage_data in stages_data:
                    ProjectStage.objects.create(
                        project=project,
                        **stage_data
                    )
