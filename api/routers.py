"""
API Routers Configuration
Centralized router setup for all model viewsets
"""
from rest_framework import routers
from api.views.projects import ProjectViewSet, ProjectStageViewSet
from api.views.bq import BQSectionViewSet, BQElementViewSet, BQItemViewSet
from api.views.consultants import (
    ConsultantViewSet, ConsultantFeeViewSet, ConsultantPaymentViewSet
)
from api.views.suppliers import (
    SupplierViewSet, LocalPurchaseOrderViewSet, SupplierInvoiceViewSet
)
from api.views.workers import WorkerViewSet, DailyLabourRecordViewSet
from api.views.ledger import ExpenseViewSet, ExpenseAllocationViewSet
from api.views.clients import ClientPaymentViewSet, ClientReceiptViewSet
from api.views.documents import DocumentViewSet, ProjectDocumentViewSet, ObjectDocumentViewSet
from api.views.media import ProjectPhotoViewSet
from api.views.approvals import ProjectApprovalViewSet
from api.views.workflows import ApprovalViewSet, ProjectActivityViewSet
from api.views.valuations import ValuationViewSet, BQItemProgressViewSet
from api.views.site_operations import (
    DailySiteReportViewSet, MaterialDeliveryViewSet, SiteIssueViewSet
)
from api.views.portfolio import PortfolioViewSet, ProjectMetricsViewSet
from api.views.cashflow import ProjectCashFlowViewSet, PortfolioCashFlowViewSet
from api.views.variations import VariationOrderViewSet, ProjectVariationViewSet


# Create a router and register all viewsets
router = routers.DefaultRouter()

# Projects
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'project-stages', ProjectStageViewSet, basename='projectstage')

# BQ (Bill of Quantities)
router.register(r'bq-sections', BQSectionViewSet, basename='bqsection')
router.register(r'bq-elements', BQElementViewSet, basename='bqelement')
router.register(r'bq-items', BQItemViewSet, basename='bqitem')

# Consultants
router.register(r'consultants', ConsultantViewSet, basename='consultant')
router.register(r'consultant-fees', ConsultantFeeViewSet, basename='consultantfee')
router.register(r'consultant-payments', ConsultantPaymentViewSet, basename='consultantpayment')

# Suppliers
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchase-orders', LocalPurchaseOrderViewSet, basename='purchaseorder')
router.register(r'supplier-invoices', SupplierInvoiceViewSet, basename='supplierinvoice')

# Workers
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'labour-records', DailyLabourRecordViewSet, basename='labourrecord')

# Ledger
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'expense-allocations', ExpenseAllocationViewSet, basename='expenseallocation')

# Clients
router.register(r'client-payments', ClientPaymentViewSet, basename='clientpayment')
router.register(r'client-receipts', ClientReceiptViewSet, basename='clientreceipt')

# Documents
router.register(r'documents', DocumentViewSet, basename='document')

# Media
router.register(r'photos', ProjectPhotoViewSet, basename='projectphoto')

# Approvals
router.register(r'approvals', ProjectApprovalViewSet, basename='projectapproval')

# Workflows
router.register(r'workflow-approvals', ApprovalViewSet, basename='approval')
router.register(r'activities', ProjectActivityViewSet, basename='projectactivity')

# Valuations
router.register(r'valuations', ValuationViewSet, basename='valuation')
router.register(r'bq-progress', BQItemProgressViewSet, basename='bqprogress')

# Site Operations
router.register(r'site-reports', DailySiteReportViewSet, basename='sitereport')
router.register(r'material-deliveries', MaterialDeliveryViewSet, basename='materialdelivery')
router.register(r'site-issues', SiteIssueViewSet, basename='siteissue')

# Portfolio Analytics
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')
router.register(r'project-metrics', ProjectMetricsViewSet, basename='projectmetrics')

# Cash Flow Forecasting
router.register(r'cashflow/project', ProjectCashFlowViewSet, basename='cashflow-project')
router.register(r'cashflow/portfolio', PortfolioCashFlowViewSet, basename='cashflow-portfolio')

# Variation Orders (Change Management)
router.register(r'variations', VariationOrderViewSet, basename='variation')
router.register(r'projects', ProjectVariationViewSet, basename='project-variations')
