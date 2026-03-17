"""Centralized, concurrency-safe code generation helpers."""

from __future__ import annotations

from typing import Optional, Tuple

from django.db import transaction
from django.utils import timezone

from apps.projects.models import Project
from apps.subcontracts.models import SubcontractAgreement, SubcontractClaim
from apps.suppliers.models import LocalPurchaseOrder
from apps.variations.models import VariationOrder


def generate_project_code(organization, year: Optional[int] = None) -> Tuple[str, int, int]:
    year = year or timezone.now().year

    with transaction.atomic():
        last = Project.objects.select_for_update().filter(
            organization=organization,
            year=year,
        ).order_by('-sequence').first()

        sequence = (last.sequence if last else 0) + 1
        code = f"PRJ-{year}-{sequence:03d}"
        return code, sequence, year


def generate_contract_code(organization, year: Optional[int] = None) -> Tuple[str, int, int]:
    year = year or timezone.now().year

    with transaction.atomic():
        last = SubcontractAgreement.objects.select_for_update().filter(
            organization=organization,
            year=year,
        ).order_by('-sequence').first()

        sequence = (last.sequence if last else 0) + 1
        code = f"SC-{year}-{sequence:03d}"
        return code, sequence, year


def generate_variation_code(project: Project) -> Tuple[str, int, None]:
    with transaction.atomic():
        last = VariationOrder.objects.select_for_update().filter(
            project=project,
        ).order_by('-sequence').first()

        sequence = (last.sequence if last else 0) + 1
        code = f"VO-{project.code}-{sequence:03d}"
        return code, sequence, None


def generate_claim_code(project: Project) -> Tuple[str, int, None]:
    with transaction.atomic():
        last = SubcontractClaim.objects.select_for_update().filter(
            project=project,
        ).order_by('-sequence').first()

        sequence = (last.sequence if last else 0) + 1
        code = f"CL-{project.code}-{sequence:03d}"
        return code, sequence, None


def generate_lpo_number(project: Project) -> Tuple[str, int, None]:
    with transaction.atomic():
        last = LocalPurchaseOrder.objects.select_for_update().filter(
            project=project,
        ).order_by('-sequence').first()

        sequence = (last.sequence if last else 0) + 1
        code = f"LPO-{project.code}-{sequence:03d}"
        return code, sequence, None


def generate_report_code(organization, year: Optional[int] = None) -> Tuple[str, int, int]:
    """Generate organization-scoped report code (RPT-YYYY-NNN)"""
    from apps.reporting.models import Report
    
    year = year or timezone.now().year

    with transaction.atomic():
        last = Report.objects.select_for_update().filter(
            organization=organization,
            year=year,
        ).order_by('-sequence').first()

        sequence = (last.sequence if last else 0) + 1
        code = f"RPT-{year}-{sequence:03d}"
        return code, sequence, year