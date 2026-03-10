"""
Bill of Quantities (BQ) Models for COMS
Manages project budgets with hierarchical structure: Section → Element → Item
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.projects.models import Project


class BQSection(models.Model):
    """
    Top-level grouping in Bill of Quantities (e.g., Substructure, Superstructure)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='bq_sections'
    )
    name = models.CharField(max_length=200, help_text=_("Section name (e.g., Substructure)"))
    order = models.IntegerField(
        default=0,
        help_text=_("Display order")
    )
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bq_sections'
        verbose_name = _('BQ Section')
        verbose_name_plural = _('BQ Sections')
        ordering = ['project', 'order', 'name']
        unique_together = [['project', 'name']]
        indexes = [
            models.Index(fields=['project', 'order']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.name}"
    
    @property
    def total_amount(self):
        """Calculate total amount for this section"""
        total = 0
        for element in self.elements.all():
            total += element.total_amount
        return total


class BQElement(models.Model):
    """
    Mid-level grouping in BQ (e.g., Foundation, Columns, Beams)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(
        BQSection,
        on_delete=models.CASCADE,
        related_name='elements'
    )
    name = models.CharField(max_length=200, help_text=_("Element name (e.g., Foundation)"))
    order = models.IntegerField(
        default=0,
        help_text=_("Display order within section")
    )
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bq_elements'
        verbose_name = _('BQ Element')
        verbose_name_plural = _('BQ Elements')
        ordering = ['section', 'order', 'name']
        unique_together = [['section', 'name']]
        indexes = [
            models.Index(fields=['section', 'order']),
        ]
    
    def __str__(self):
        return f"{self.section.name} → {self.name}"
    
    @property
    def total_amount(self):
        """Calculate total amount for this element"""
        total = 0
        for item in self.items.all():
            total += item.amount
        return total


class BQItem(models.Model):
    """
    Individual line items in the Bill of Quantities
    Amount is calculated as: quantity × rate
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    element = models.ForeignKey(
        BQElement,
        on_delete=models.CASCADE,
        related_name='items'
    )
    description = models.TextField(help_text=_("Detailed item description"))
    unit = models.CharField(
        max_length=50,
        help_text=_("Unit of measurement (e.g., m², m³, m, No.)")
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Quantity per unit")
    )
    rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Rate per unit")
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_("Total amount (quantity × rate)")
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bq_items'
        verbose_name = _('BQ Item')
        verbose_name_plural = _('BQ Items')
        ordering = ['element', 'id']
        indexes = [
            models.Index(fields=['element']),
        ]
    
    def __str__(self):
        return f"{self.description[:50]} - {self.quantity} {self.unit}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate amount before saving"""
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)
