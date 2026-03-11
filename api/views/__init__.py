"""
API ViewSets
Centralized imports for all model viewsets
"""
from .projects import ProjectViewSet, ProjectStageViewSet
from .bq import BQSectionViewSet, BQElementViewSet, BQItemViewSet
from .consultants import ConsultantViewSet, ConsultantFeeViewSet, ConsultantPaymentViewSet
from .suppliers import SupplierViewSet, LocalPurchaseOrderViewSet, SupplierInvoiceViewSet
from .workers import WorkerViewSet, DailyLabourRecordViewSet
from .ledger import ExpenseViewSet, ExpenseAllocationViewSet
from .clients import ClientPaymentViewSet, ClientReceiptViewSet
from .documents import DocumentViewSet, DocumentVersionViewSet
from .media import ProjectPhotoViewSet
from .approvals import ProjectApprovalViewSet

__all__ = [
    # Projects
    'ProjectViewSet',
    'ProjectStageViewSet',
    # BQ
    'BQSectionViewSet',
    'BQElementViewSet',
    'BQItemViewSet',
    # Consultants
    'ConsultantViewSet',
    'ConsultantFeeViewSet',
    'ConsultantPaymentViewSet',
    # Suppliers
    'SupplierViewSet',
    'LocalPurchaseOrderViewSet',
    'SupplierInvoiceViewSet',
    # Workers
    'WorkerViewSet',
    'DailyLabourRecordViewSet',
    # Ledger
    'ExpenseViewSet',
    'ExpenseAllocationViewSet',
    # Clients
    'ClientPaymentViewSet',
    'ClientReceiptViewSet',
    # Documents
    'DocumentViewSet',
    'DocumentVersionViewSet',
    # Media
    'ProjectPhotoViewSet',
    # Approvals
    'ProjectApprovalViewSet',
]
