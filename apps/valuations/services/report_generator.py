"""
PDF Report Generation for Valuations
Uses WeasyPrint to generate professional IPC reports
"""
from io import BytesIO
from decimal import Decimal
from typing import Dict, Any
from django.template.loader import render_to_string
from django.http import HttpResponse

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


def generate_valuation_pdf(valuation_id: str) -> BytesIO:
    """
    Generate PDF report for a valuation.
    
    Args:
        valuation_id: Valuation UUID
        
    Returns:
        BytesIO object containing PDF data
        
    Raises:
        ImportError: If WeasyPrint is not installed
    """
    if not WEASYPRINT_AVAILABLE:
        raise ImportError(
            "WeasyPrint is required for PDF generation. "
            "Install it with: pip install weasyprint"
        )
    
    from apps.valuations.services import ValuationService
    
    # Get report data
    report_data = ValuationService.get_valuation_report_data(valuation_id)
    
    # Render HTML template
    html_string = render_to_string(
        'valuations/valuation_report.html',
        report_data
    )
    
    # Generate PDF
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    return pdf_file


def generate_valuation_pdf_response(valuation_id: str, filename: str = None) -> HttpResponse:
    """
    Generate PDF and return as HTTP response for download.
    
    Args:
        valuation_id: Valuation UUID
        filename: Optional custom filename (default: valuation_number.pdf)
        
    Returns:
        HttpResponse with PDF content
    """
    from apps.valuations.models import Valuation
    
    valuation = Valuation.objects.get(id=valuation_id)
    
    if filename is None:
        filename = f"{valuation.valuation_number}.pdf"
    
    pdf_file = generate_valuation_pdf(valuation_id)
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def generate_simple_valuation_report(valuation_id: str) -> str:
    """
    Generate simple text-based valuation report (fallback if WeasyPrint unavailable).
    
    Args:
        valuation_id: Valuation UUID
        
    Returns:
        Text report as string
    """
    from apps.valuations.services import ValuationService
    from apps.valuations.models import Valuation
    
    valuation = Valuation.objects.get(id=valuation_id)
    report_data = ValuationService.get_valuation_report_data(valuation_id)
    
    report = []
    report.append("=" * 80)
    report.append("INTERIM PAYMENT CERTIFICATE (IPC)")
    report.append("=" * 80)
    report.append("")
    report.append(f"Valuation Number: {valuation.valuation_number}")
    report.append(f"Date: {valuation.valuation_date}")
    report.append(f"Project: {valuation.project.name} ({valuation.project.code})")
    report.append(f"Client: {valuation.project.client_name}")
    report.append("")
    report.append("-" * 80)
    report.append("FINANCIAL SUMMARY")
    report.append("-" * 80)
    report.append(f"Work Completed Value:  KES {valuation.work_completed_value:,.2f}")
    report.append(f"Previous Payments:     KES {valuation.previous_payments:,.2f}")
    report.append(f"Gross Amount:          KES {valuation.gross_amount:,.2f}")
    report.append(f"Retention ({valuation.retention_percentage}%):    KES {valuation.retention_amount:,.2f}")
    report.append(f"Amount Due:            KES {valuation.amount_due:,.2f}")
    report.append("")
    report.append("-" * 80)
    report.append("BQ ITEMS")
    report.append("-" * 80)
    
    for section_data in report_data['items_grouped']:
        section = section_data['section']
        report.append(f"\n{section.name}")
        report.append("-" * 80)
        
        for element_data in section_data['elements']:
            element = element_data['element']
            report.append(f"\n  {element.name}")
            
            for item_data in element_data['items']:
                progress = item_data['progress']
                bq_item = item_data['bq_item']
                report.append(f"    {bq_item.description[:60]}")
                report.append(f"      Quantity: {progress.cumulative_quantity} {bq_item.unit}")
                report.append(f"      Value: KES {progress.cumulative_value:,.2f}")
    
    report.append("")
    report.append("=" * 80)
    report.append(f"Status: {valuation.get_status_display()}")
    if valuation.approved_by:
        report.append(f"Approved By: {valuation.approved_by.get_full_name()}")
        report.append(f"Approved Date: {valuation.approved_date}")
    report.append("=" * 80)
    
    return "\n".join(report)
