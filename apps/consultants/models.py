"""
Consultant Models for COMS
Handles consultant management and fee tracking
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import Organization
from apps.projects.models import Project


class Consultant(models.Model):
    """
    Professional consultants working on construction projects
    """
    
    class ConsultantType(models.TextChoices):
        ARCHITECT = 'ARCHITECT', _('Architect')
        STRUCTURAL_ENGINEER = 'STRUCTURAL_ENGINEER', _('Structural Engineer')
        MECHANICAL_ENGINEER = 'MECHANICAL_ENGINEER', _('Mechanical Engineer')
        ELECTRICAL_ENGINEER = 'ELECTRICAL_ENGINEER', _('Electrical Engineer')
        QUANTITY_SURVEYOR = 'QUANTITY_SURVEYOR', _('Quantity Surveyor')
        SERVICES_ENGINEER = 'SERVICES_ENGINEER', _('Services Engineer')
        PLUMBING_ENGINEER = 'PLUMBING_ENGINEER', _('Plumbing Engineer')
        OTHER = 'OTHER', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='consultants'
    )
    name = models.CharField(max_length=200, help_text=_("Consultant name"))
    consultant_type = models.CharField(
        max_length=30,
        choices=ConsultantType.choices
    )
    company = models.CharField(max_length=200, blank=True, help_text=_("Company/Firm name"))
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultants'
        verbose_name = _('Consultant')
        verbose_name_plural = _('Consultants')
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'consultant_type']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_consultant_type_display()}"


class ProjectConsultant(models.Model):
    """
    Links consultants to projects with specific roles
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_consultants'
    )
    consultant = models.ForeignKey(
        Consultant,
        on_delete=models.PROTECT,
        related_name='project_assignments'
    )
    role = models.CharField(
        max_length=100,
        help_text=_("Role on this project (e.g., 'Lead Architect', 'Supervision Engineer')")
    )
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'project_consultants'
        verbose_name = _('Project Consultant')
        verbose_name_plural = _('Project Consultants')
        unique_together = [['project', 'consultant']]
        indexes = [
            models.Index(fields=['project', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.consultant.name}"


class ConsultantFee(models.Model):
    """
    Tracks agreed professional fees for consultants on projects
    """
    
    class FeeType(models.TextChoices):
        DESIGN = 'DESIGN', _('Design Fees')
        SUPERVISION = 'SUPERVISION', _('Supervision Fees')
        INSPECTION = 'INSPECTION', _('Inspection Fees')
        CERTIFICATION = 'CERTIFICATION', _('Certification Fees')
        CONSULTANCY = 'CONSULTANCY', _('General Consultancy')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultant = models.ForeignKey(
        Consultant,
        on_delete=models.PROTECT,
        related_name='fees'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='consultant_fees'
    )
    fee_type = models.CharField(
        max_length=20,
        choices=FeeType.choices
    )
    contract_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Total agreed fee amount")
    )
    payment_schedule = models.TextField(
        blank=True,
        help_text=_("Payment terms and schedule")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultant_fees'
        verbose_name = _('Consultant Fee')
        verbose_name_plural = _('Consultant Fees')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['consultant', 'project']),
            models.Index(fields=['project']),
        ]
    
    def __str__(self):
        return f"{self.consultant.name} - {self.project.code} - {self.get_fee_type_display()}"
    
    @property
    def total_paid(self):
        """Calculate total amount paid"""
        return self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    @property
    def outstanding_balance(self):
        """Calculate remaining balance"""
        return self.contract_amount - self.total_paid


class ConsultantPayment(models.Model):
    """
    Records payments made to consultants
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultant_fee = models.ForeignKey(
        ConsultantFee,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("e.g., Bank Transfer, Cheque, Cash")
    )
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultant_payments'
        verbose_name = _('Consultant Payment')
        verbose_name_plural = _('Consultant Payments')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['consultant_fee', 'payment_date']),
        ]
    
    def __str__(self):
        return f"{self.consultant_fee.consultant.name} - {self.amount} on {self.payment_date}"
