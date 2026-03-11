"""
API Serializers
Centralized imports for all model serializers
"""
from .projects import ProjectSerializer, ProjectStageSerializer
from .bq import BQSectionSerializer, BQElementSerializer, BQItemSerializer
from .consultants import (
    ConsultantSerializer,
    ProjectConsultantSerializer,
    ConsultantFeeSerializer,
    ConsultantPaymentSerializer
)
from .suppliers import (
    SupplierSerializer,
    LocalPurchaseOrderSerializer,
    LPOItemSerializer,
    SupplierInvoiceSerializer,
    SupplierPaymentSerializer
)
from .workers import WorkerSerializer, DailyLabourRecordSerializer
from .ledger import ExpenseSerializer, ExpenseAllocationSerializer
from .clients import ClientPaymentSerializer, ClientReceiptSerializer
from .documents import DocumentSerializer, DocumentVersionSerializer
from .media import ProjectPhotoSerializer
from .approvals import ProjectApprovalSerializer

__all__ = [
    # Projects
    'ProjectSerializer',
    'ProjectStageSerializer',
    # BQ
    'BQSectionSerializer',
    'BQElementSerializer',
    'BQItemSerializer',
    # Consultants
    'ConsultantSerializer',
    'ProjectConsultantSerializer',
    'ConsultantFeeSerializer',
    'ConsultantPaymentSerializer',
    # Suppliers
    'SupplierSerializer',
    'LocalPurchaseOrderSerializer',
    'LPOItemSerializer',
    'SupplierInvoiceSerializer',
    'SupplierPaymentSerializer',
    # Workers
    'WorkerSerializer',
    'DailyLabourRecordSerializer',
    # Ledger
    'ExpenseSerializer',
    'ExpenseAllocationSerializer',
    # Clients
    'ClientPaymentSerializer',
    'ClientReceiptSerializer',
    # Documents
    'DocumentSerializer',
    'DocumentVersionSerializer',
    # Media
    'ProjectPhotoSerializer',
    # Approvals
    'ProjectApprovalSerializer',
]
