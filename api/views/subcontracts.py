"""
Subcontractor Management - API Views

RESTful API endpoints for subcontract operations including:
- Subcontractor CRUD
- Subcontract agreement management
- Payment claim workflow
- Project-specific endpoints
- Summary statistics

All endpoints include proper permissions and validation.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.subcontracts.models import (
    Subcontractor,
    SubcontractAgreement,
    SubcontractClaim
)
from apps.subcontracts.selectors import (
    SubcontractorSelector,
    SubcontractSelector,
    ClaimSelector
)
from apps.subcontracts.services import SubcontractService
from apps.common.services import generate_claim_code, generate_contract_code
from apps.projects.models import Project
from api.serializers.subcontracts import (
    SubcontractorSerializer,
    SubcontractorBasicSerializer,
    SubcontractorCreateSerializer,
    SubcontractAgreementSerializer,
    SubcontractAgreementBasicSerializer,
    SubcontractCreateSerializer,
    SubcontractClaimSerializer,
    ClaimSubmitSerializer,
    ClaimCertifySerializer,
    ClaimRejectSerializer,
    ClaimMarkPaidSerializer,
    SubcontractSummarySerializer,
    PaymentSummarySerializer,
)


class SubcontractorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subcontractor operations.
    
    Provides complete CRUD operations for managing subcontractors.
    
    Endpoints:
        GET    /api/subcontractors/              List all subcontractors
        POST   /api/subcontractors/              Create new subcontractor
        GET    /api/subcontractors/{id}/         Get subcontractor details
        PUT    /api/subcontractors/{id}/         Update subcontractor
        PATCH  /api/subcontractors/{id}/         Partial update
        DELETE /api/subcontractors/{id}/         Delete subcontractor
        GET    /api/subcontractors/{id}/contracts/  Get contracts for subcontractor
    """
    
    queryset = SubcontractorSelector.get_base_queryset()
    serializer_class = SubcontractorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'specialization']
    search_fields = ['name', 'contact_person', 'email', 'specialization']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == 'create':
            return SubcontractorCreateSerializer
        elif self.action == 'list':
            return SubcontractorBasicSerializer
        return SubcontractorSerializer
    
    def get_queryset(self):
        """Filter queryset based on user's organization"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by organization
        queryset = queryset.filter(organization=user.organization)
        
        # Optional active filter
        active_only = self.request.query_params.get('active_only')
        if active_only and active_only.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @extend_schema(
        summary="Create new subcontractor",
        request=SubcontractorCreateSerializer,
        responses={201: SubcontractorSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create new subcontractor"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subcontractor = serializer.save()
        
        # Return full data
        output_serializer = SubcontractorSerializer(
            subcontractor,
            context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Get subcontractor's contracts",
        responses={200: SubcontractAgreementBasicSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='contracts')
    def contracts(self, request, pk=None):
        """
        GET /api/subcontractors/{id}/contracts/
        
        Get all contracts for this subcontractor.
        """
        subcontractor = self.get_object()
        
        contracts = SubcontractSelector.get_subcontractor_contracts(
            subcontractor=subcontractor
        )
        
        serializer = SubcontractAgreementBasicSerializer(
            contracts,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class SubcontractViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subcontract Agreement operations.
    
    Provides CRUD and workflow management for subcontracts.
    
    Endpoints:
        GET    /api/subcontracts/                    List all subcontracts
        POST   /api/subcontracts/                    Create new subcontract
        GET    /api/subcontracts/{id}/               Get subcontract details
        PUT    /api/subcontracts/{id}/               Update subcontract
        DELETE /api/subcontracts/{id}/               Delete subcontract
        POST   /api/subcontracts/{id}/activate/      Activate subcontract
        POST   /api/subcontracts/{id}/complete/      Complete subcontract
        GET    /api/subcontracts/{id}/payment-summary/  Get payment summary
    """
    
    queryset = SubcontractSelector.get_base_queryset()
    serializer_class = SubcontractAgreementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'subcontractor', 'status']
    search_fields = ['contract_reference', 'scope_of_work', 'subcontractor__name']
    ordering_fields = ['created_at', 'start_date', 'contract_value']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == 'create':
            return SubcontractCreateSerializer
        elif self.action == 'list':
            return SubcontractAgreementBasicSerializer
        return SubcontractAgreementSerializer
    
    def get_queryset(self):
        """Filter queryset based on permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by organization
        queryset = queryset.filter(project__organization=user.organization)
        
        # Optional project filter
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset

    @extend_schema(
        summary="Preview next subcontract reference",
        description="Returns the next generated subcontract contract reference for the current organization.",
    )
    @action(detail=False, methods=['get'], url_path='next-reference')
    def next_reference(self, request):
        organization = getattr(request.user, 'organization', None)
        if organization is None:
            return Response({'detail': 'Organization scope is required.'}, status=status.HTTP_400_BAD_REQUEST)

        contract_reference, sequence, year = generate_contract_code(organization)
        return Response(
            {
                'contract_reference': contract_reference,
                'sequence': sequence,
                'year': year,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(
        summary="Create new subcontract",
        request=SubcontractCreateSerializer,
        responses={201: SubcontractAgreementSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create new subcontract agreement"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subcontract = serializer.save()
        
        # Return full data
        output_serializer = SubcontractAgreementSerializer(
            subcontract,
            context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Activate subcontract",
        description="Activate a draft subcontract to make it active",
        responses={200: SubcontractAgreementSerializer}
    )
    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        """
        POST /api/subcontracts/{id}/activate/
        
        Activate a DRAFT subcontract.
        """
        subcontract = self.get_object()
        
        activated = SubcontractService.activate_subcontract(
            subcontract=subcontract,
            activated_by=request.user
        )
        
        serializer = SubcontractAgreementSerializer(
            activated,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        summary="Complete subcontract",
        description="Mark subcontract as completed",
        responses={200: SubcontractAgreementSerializer}
    )
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        POST /api/subcontracts/{id}/complete/
        
        Mark subcontract as COMPLETED.
        """
        subcontract = self.get_object()
        
        completed = SubcontractService.complete_subcontract(
            subcontract=subcontract,
            completed_by=request.user
        )
        
        serializer = SubcontractAgreementSerializer(
            completed,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get payment summary",
        description="Get comprehensive payment summary for this subcontract",
        responses={200: PaymentSummarySerializer}
    )
    @action(detail=True, methods=['get'], url_path='payment-summary')
    def payment_summary(self, request, pk=None):
        """
        GET /api/subcontracts/{id}/payment-summary/
        
        Get payment summary with all financial details.
        """
        subcontract = self.get_object()
        
        summary = ClaimSelector.get_subcontract_payment_summary(subcontract)
        
        serializer = PaymentSummarySerializer(summary)
        return Response(serializer.data)


class SubcontractClaimViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subcontract Claim operations.
    
    Provides CRUD and workflow management for payment claims.
    
    Endpoints:
        GET    /api/subcontract-claims/              List all claims
        POST   /api/subcontract-claims/              Submit new claim
        GET    /api/subcontract-claims/{id}/         Get claim details
        PUT    /api/subcontract-claims/{id}/         Update claim
        DELETE /api/subcontract-claims/{id}/         Delete claim
        POST   /api/subcontract-claims/{id}/submit/  Submit claim
        POST   /api/subcontract-claims/{id}/certify/ Certify claim
        POST   /api/subcontract-claims/{id}/reject/  Reject claim
        POST   /api/subcontract-claims/{id}/mark-paid/  Mark as paid
        GET    /api/subcontract-claims/pending/      Get pending claims
    """
    
    queryset = ClaimSelector.get_base_queryset()
    serializer_class = SubcontractClaimSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subcontract', 'status']
    search_fields = ['claim_number', 'description']
    ordering_fields = ['created_at', 'submitted_date', 'certified_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == 'create':
            return ClaimSubmitSerializer
        elif self.action == 'certify':
            return ClaimCertifySerializer
        elif self.action == 'reject':
            return ClaimRejectSerializer
        elif self.action == 'mark_paid':
            return ClaimMarkPaidSerializer
        return SubcontractClaimSerializer
    
    def get_queryset(self):
        """Filter queryset based on permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by organization
        queryset = queryset.filter(
            subcontract__project__organization=user.organization
        )
        
        # Optional filters
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(subcontract__project_id=project_id)
        
        subcontract_id = self.request.query_params.get('subcontract')
        if subcontract_id:
            queryset = queryset.filter(subcontract_id=subcontract_id)
        
        return queryset

    @extend_schema(
        summary="Preview next subcontract claim number",
        description="Returns the next generated claim number for a selected project.",
        parameters=[
            OpenApiParameter(
                name='project_id',
                type=str,
                description='Project UUID',
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='next-number')
    def next_number(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'detail': 'project_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id, organization=request.user.organization)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        claim_number, sequence, _ = generate_claim_code(project)
        return Response(
            {
                'claim_number': claim_number,
                'sequence': sequence,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(
        summary="Submit new claim",
        request=ClaimSubmitSerializer,
        responses={201: SubcontractClaimSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Submit new payment claim"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        claim = serializer.save()
        
        # Return full data
        output_serializer = SubcontractClaimSerializer(
            claim,
            context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Certify payment claim",
        description="Certify a submitted claim for payment",
        request=ClaimCertifySerializer,
        responses={200: SubcontractClaimSerializer}
    )
    @action(detail=True, methods=['post'], url_path='certify')
    def certify(self, request, pk=None):
        """
        POST /api/subcontract-claims/{id}/certify/
        
        Certify a SUBMITTED claim.
        
        Body:
        {
            "certified_amount": "480000.00",
            "notes": "Approved with 4% deduction"
        }
        """
        claim = self.get_object()
        
        serializer = ClaimCertifySerializer(
            claim,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        certified_claim = serializer.save()
        
        output_serializer = SubcontractClaimSerializer(
            certified_claim,
            context={'request': request}
        )
        return Response(output_serializer.data)
    
    @extend_schema(
        summary="Reject payment claim",
        description="Reject a submitted claim",
        request=ClaimRejectSerializer,
        responses={200: SubcontractClaimSerializer}
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """
        POST /api/subcontract-claims/{id}/reject/
        
        Reject a SUBMITTED claim.
        
        Body:
        {
            "rejection_reason": "Incomplete documentation"
        }
        """
        claim = self.get_object()
        
        serializer = ClaimRejectSerializer(
            claim,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        rejected_claim = serializer.save()
        
        output_serializer = SubcontractClaimSerializer(
            rejected_claim,
            context={'request': request}
        )
        return Response(output_serializer.data)
    
    @extend_schema(
        summary="Mark claim as paid",
        description="Mark a certified claim as paid",
        request=ClaimMarkPaidSerializer,
        responses={200: SubcontractClaimSerializer}
    )
    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        """
        POST /api/subcontract-claims/{id}/mark-paid/
        
        Mark a CERTIFIED claim as PAID.
        
        Body:
        {
            "payment_reference": "PAY-2026-12345"
        }
        """
        claim = self.get_object()
        
        serializer = ClaimMarkPaidSerializer(
            claim,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        paid_claim = serializer.save()
        
        output_serializer = SubcontractClaimSerializer(
            paid_claim,
            context={'request': request}
        )
        return Response(output_serializer.data)
    
    @extend_schema(
        summary="Get pending claims",
        description="Get all pending claims (awaiting certification or payment)",
        parameters=[
            OpenApiParameter(
                name='project',
                type=str,
                description='Filter by project ID'
            ),
        ],
        responses={200: SubcontractClaimSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """
        GET /api/subcontract-claims/pending/
        
        Get all pending claims.
        
        Query params:
        - project: Filter by project ID
        """
        project_id = request.query_params.get('project')
        project = None
        
        if project_id:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                pass
        
        claims = ClaimSelector.get_pending_claims(
            project=project,
            organization=request.user.organization
        )
        
        serializer = SubcontractClaimSerializer(
            claims,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class ProjectSubcontractViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for project-specific subcontract access.
    
    Nested under projects endpoint:
        GET /api/projects/{project_id}/subcontracts/
        GET /api/projects/{project_id}/subcontracts/{id}/
        GET /api/projects/{project_id}/subcontracts/summary/
    """
    serializer_class = SubcontractAgreementBasicSerializer
    
    def get_queryset(self):
        """Get subcontracts for specific project"""
        project_id = self.kwargs.get('project_pk')
        return SubcontractSelector.get_project_subcontracts(
            project_id=project_id
        )
    
    @extend_schema(
        summary="Get project subcontract summary",
        responses={200: SubcontractSummarySerializer}
    )
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request, project_pk=None):
        """
        GET /api/projects/{project_id}/subcontracts/summary/
        
        Get summary statistics for project subcontracts.
        """
        from apps.projects.models import Project
        
        try:
            project = Project.objects.get(id=project_pk)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Project not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        summary = SubcontractSelector.get_subcontract_summary(project)
        
        serializer = SubcontractSummarySerializer(summary)
        return Response(serializer.data)


class ProjectClaimViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for project-specific claim access.
    
    Nested under projects endpoint:
        GET /api/projects/{project_id}/subcontract-claims/
        GET /api/projects/{project_id}/subcontract-claims/{id}/
    """
    serializer_class = SubcontractClaimSerializer
    
    def get_queryset(self):
        """Get claims for specific project"""
        project_id = self.kwargs.get('project_pk')
        
        from apps.projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return SubcontractClaim.objects.none()
        
        return ClaimSelector.get_project_claims(project=project)
