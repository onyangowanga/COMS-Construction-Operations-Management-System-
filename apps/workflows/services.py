"""Workflow Engine service layer for reusable module transitions."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from django.db import transaction
from django.utils import timezone

from apps.authentication.models import User
from apps.roles.models import UserRole
from apps.notifications.services import NotificationService
from api.services.activity_service import log_activity
from apps.workflows.models import (
    ProjectActivity,
    WorkflowDefinition,
    WorkflowHistory,
    WorkflowInstance,
    WorkflowState,
    WorkflowTransition,
)


class WorkflowEngineError(Exception):
    """Workflow operation error."""


class WorkflowEngineService:
    """Reusable workflow engine for module state transitions."""

    MODULE_ALIASES = {
        'variation': WorkflowDefinition.Module.VARIATION,
        'variations': WorkflowDefinition.Module.VARIATION,
        'procurement': WorkflowDefinition.Module.PROCUREMENT,
        'purchase_order': WorkflowDefinition.Module.PROCUREMENT,
        'claim': WorkflowDefinition.Module.CLAIM,
        'claims': WorkflowDefinition.Module.CLAIM,
        'contract': WorkflowDefinition.Module.CONTRACT,
        'contracts': WorkflowDefinition.Module.CONTRACT,
    }

    DEFAULT_WORKFLOWS: Dict[str, Dict[str, Any]] = {
        WorkflowDefinition.Module.VARIATION: {
            'name': 'Variation Approval Workflow',
            'states': [
                ('DRAFT', True, False),
                ('SUBMITTED', False, False),
                ('APPROVED', False, True),
                ('REJECTED', False, True),
            ],
            'transitions': [
                ('DRAFT', 'SUBMITTED', 'submit', ['super_admin', 'staff', 'site_manager', 'contractor']),
                ('SUBMITTED', 'APPROVED', 'approve', ['super_admin', 'qs', 'architect', 'site_manager']),
                ('SUBMITTED', 'REJECTED', 'reject', ['super_admin', 'qs', 'architect', 'site_manager']),
                ('SUBMITTED', 'SUBMITTED', 'certify', ['super_admin', 'qs', 'architect']),
                ('APPROVED', 'APPROVED', 'certify', ['super_admin', 'qs', 'architect']),
            ],
        },
        WorkflowDefinition.Module.PROCUREMENT: {
            'name': 'Procurement LPO Workflow',
            'states': [
                ('DRAFT', True, False),
                ('APPROVED', False, False),
                ('ISSUED', False, False),
                ('DELIVERED', False, False),
                ('INVOICED', False, False),
                ('PAID', False, True),
                ('CANCELLED', False, True),
            ],
            'transitions': [
                ('DRAFT', 'APPROVED', 'submit', ['super_admin', 'site_manager', 'staff', 'contractor']),
                ('DRAFT', 'APPROVED', 'approve', ['super_admin', 'site_manager', 'staff', 'contractor']),
                ('APPROVED', 'ISSUED', 'issue', ['super_admin', 'site_manager', 'staff']),
                ('APPROVED', 'DELIVERED', 'deliver', ['super_admin', 'site_manager', 'staff']),
                ('ISSUED', 'DELIVERED', 'deliver', ['super_admin', 'site_manager', 'staff']),
                ('DELIVERED', 'INVOICED', 'invoice', ['super_admin', 'finance_manager', 'staff']),
                ('INVOICED', 'PAID', 'pay', ['super_admin', 'finance_manager', 'staff']),
            ],
        },
        WorkflowDefinition.Module.CLAIM: {
            'name': 'Claim Certification Workflow',
            'states': [
                ('DRAFT', True, False),
                ('SUBMITTED', False, False),
                ('CERTIFIED', False, False),
                ('PAID', False, True),
                ('REJECTED', False, True),
            ],
            'transitions': [
                ('DRAFT', 'SUBMITTED', 'submit', ['super_admin', 'subcontractor', 'staff', 'site_manager']),
                ('SUBMITTED', 'CERTIFIED', 'certify', ['super_admin', 'qs', 'architect', 'site_manager']),
                ('SUBMITTED', 'REJECTED', 'reject', ['super_admin', 'qs', 'architect', 'site_manager']),
                ('CERTIFIED', 'PAID', 'pay', ['super_admin', 'finance_manager', 'staff']),
            ],
        },
        WorkflowDefinition.Module.CONTRACT: {
            'name': 'Contract Lifecycle Workflow',
            'states': [
                ('DRAFT', True, False),
                ('ACTIVE', False, False),
                ('COMPLETED', False, True),
                ('TERMINATED', False, True),
            ],
            'transitions': [
                ('DRAFT', 'ACTIVE', 'activate', ['super_admin', 'site_manager', 'staff']),
                ('ACTIVE', 'COMPLETED', 'complete', ['super_admin', 'site_manager', 'staff']),
                ('ACTIVE', 'TERMINATED', 'terminate', ['super_admin', 'site_manager']),
            ],
        },
    }

    @classmethod
    def normalize_module(cls, module: str) -> str:
        normalized = (module or '').strip().lower()
        mapped = cls.MODULE_ALIASES.get(normalized, normalized.upper())
        valid = {choice[0] for choice in WorkflowDefinition.Module.choices}
        if mapped not in valid:
            raise WorkflowEngineError(f'Unsupported workflow module: {module}')
        return mapped

    @classmethod
    def get_workflow_for_module(cls, module: str) -> WorkflowDefinition:
        module_code = cls.normalize_module(module)
        definition = WorkflowDefinition.objects.filter(module=module_code, is_active=True).first()
        if definition:
            return definition
        return cls._bootstrap_default_workflow(module_code)

    @classmethod
    @transaction.atomic
    def _bootstrap_default_workflow(cls, module_code: str) -> WorkflowDefinition:
        config = cls.DEFAULT_WORKFLOWS[module_code]
        workflow, _ = WorkflowDefinition.objects.get_or_create(
            module=module_code,
            name=config['name'],
            defaults={'is_active': True},
        )

        state_lookup: Dict[str, WorkflowState] = {}
        for index, (state_name, is_initial, is_terminal) in enumerate(config['states']):
            state, _ = WorkflowState.objects.get_or_create(
                workflow=workflow,
                name=state_name,
                defaults={
                    'is_initial': is_initial,
                    'is_terminal': is_terminal,
                    'sort_order': index,
                },
            )
            if state.is_initial != is_initial or state.is_terminal != is_terminal or state.sort_order != index:
                state.is_initial = is_initial
                state.is_terminal = is_terminal
                state.sort_order = index
                state.save(update_fields=['is_initial', 'is_terminal', 'sort_order'])
            state_lookup[state_name] = state

        for from_state, to_state, action, roles in config['transitions']:
            WorkflowTransition.objects.get_or_create(
                workflow=workflow,
                from_state=state_lookup[from_state],
                to_state=state_lookup[to_state],
                action=action,
                defaults={'allowed_roles': roles},
            )

        return workflow

    @classmethod
    def _resolve_entity(cls, module_code: str, entity_id: str):
        if module_code == WorkflowDefinition.Module.VARIATION:
            from apps.variations.models import VariationOrder

            return VariationOrder.objects.select_related('project', 'project__organization').get(id=entity_id)

        if module_code == WorkflowDefinition.Module.PROCUREMENT:
            from apps.suppliers.models import LocalPurchaseOrder

            return LocalPurchaseOrder.objects.select_related('project', 'project__organization').get(id=entity_id)

        if module_code == WorkflowDefinition.Module.CLAIM:
            from apps.subcontracts.models import SubcontractClaim

            return SubcontractClaim.objects.select_related('project', 'project__organization').get(id=entity_id)

        if module_code == WorkflowDefinition.Module.CONTRACT:
            from apps.subcontracts.models import SubcontractAgreement

            return SubcontractAgreement.objects.select_related('project', 'project__organization').get(id=entity_id)

        raise WorkflowEngineError(f'Unsupported module resolver: {module_code}')

    @classmethod
    def _entity_state_name(cls, module_code: str, entity) -> str:
        if module_code in {
            WorkflowDefinition.Module.VARIATION,
            WorkflowDefinition.Module.PROCUREMENT,
            WorkflowDefinition.Module.CLAIM,
            WorkflowDefinition.Module.CONTRACT,
        }:
            return str(entity.status)
        raise WorkflowEngineError(f'State mapping not implemented for module: {module_code}')

    @classmethod
    def _entity_project_id(cls, entity):
        if hasattr(entity, 'project_id') and entity.project_id:
            return entity.project_id
        if hasattr(entity, 'project') and entity.project:
            return entity.project.id
        return None

    @classmethod
    def _entity_reference(cls, module_code: str, entity) -> str:
        if module_code == WorkflowDefinition.Module.VARIATION:
            return getattr(entity, 'reference_number', str(entity.id))
        if module_code == WorkflowDefinition.Module.PROCUREMENT:
            return getattr(entity, 'lpo_number', str(entity.id))
        if module_code == WorkflowDefinition.Module.CLAIM:
            return getattr(entity, 'claim_number', str(entity.id))
        if module_code == WorkflowDefinition.Module.CONTRACT:
            return getattr(entity, 'contract_reference', str(entity.id))
        return str(entity.id)

    @classmethod
    def initialize_workflow(cls, module: str, entity_id: str, user: User | None = None) -> WorkflowInstance:
        module_code = cls.normalize_module(module)
        workflow = cls.get_workflow_for_module(module_code)
        entity = cls._resolve_entity(module_code, entity_id)
        status_name = cls._entity_state_name(module_code, entity)

        state = WorkflowState.objects.filter(workflow=workflow, name=status_name).first()
        if not state:
            state = WorkflowState.objects.filter(workflow=workflow, is_initial=True).first()
        if not state:
            raise WorkflowEngineError(f'Workflow has no initial state configured for module {module_code}')

        instance, created = WorkflowInstance.objects.get_or_create(
            module=module_code,
            entity_id=entity.id,
            defaults={
                'workflow': workflow,
                'current_state': state,
                'last_transition_by': user,
                'last_transition_at': timezone.now() if user else None,
            },
        )

        if created:
            WorkflowHistory.objects.create(
                instance=instance,
                from_state=None,
                to_state=state,
                action='initialize',
                performed_by=user,
                comment='Workflow initialized',
            )

        return instance

    @classmethod
    def _get_user_roles(cls, user: User) -> set[str]:
        roles = {str(getattr(user, 'system_role', '') or '').lower()}
        db_roles = UserRole.objects.filter(user=user, is_active=True).select_related('role')
        for user_role in db_roles:
            if user_role.role and user_role.role.code:
                roles.add(user_role.role.code.lower())
        if getattr(user, 'is_superuser', False):
            roles.add('super_admin')
            roles.add('admin')
        return {r for r in roles if r}

    @classmethod
    def get_available_transitions(cls, user: User, module: str, entity_id: str) -> List[WorkflowTransition]:
        instance = cls.initialize_workflow(module=module, entity_id=entity_id, user=user)
        transitions = WorkflowTransition.objects.filter(
            workflow=instance.workflow,
            from_state=instance.current_state,
        ).select_related('to_state', 'from_state')

        user_roles = cls._get_user_roles(user)
        allowed = []
        for transition in transitions:
            required_roles = {str(role).lower() for role in (transition.allowed_roles or [])}
            if not required_roles or user_roles.intersection(required_roles):
                allowed.append(transition)
        return allowed

    @classmethod
    def _notify_transition(cls, instance: WorkflowInstance, actor: User, action: str, comment: str = ''):
        transitions = WorkflowTransition.objects.filter(
            workflow=instance.workflow,
            from_state=instance.current_state,
        )

        role_targets = set()
        for transition in transitions:
            role_targets.update({str(role).lower() for role in (transition.allowed_roles or [])})

        organization = getattr(actor, 'organization', None)
        if organization is None:
            return

        candidate_users = User.objects.filter(is_active=True, organization=organization).exclude(id=actor.id)
        if role_targets:
            candidate_users = candidate_users.filter(system_role__in=role_targets)

        module_name = instance.get_module_display()
        entity_ref = str(instance.entity_id)

        for target in candidate_users.distinct()[:20]:
            NotificationService.create_notification(
                user=target,
                title=f'{module_name} pending action',
                message=(
                    f'{module_name} {entity_ref} transitioned via "{action}" to '
                    f'{instance.current_state.name}. Review and take next action if required.'
                ),
                notification_type='workflow',
                priority='normal',
                metadata={
                    'module': instance.module,
                    'entity_id': str(instance.entity_id),
                    'state': instance.current_state.name,
                },
                action_url=f'/workflows?module={instance.module}&entity_id={instance.entity_id}',
                action_label='Open Workflow',
            )

        NotificationService.create_notification(
            user=actor,
            title='Workflow transition recorded',
            message=f'Your action "{action}" was applied successfully.',
            notification_type='workflow',
            priority='low',
            metadata={
                'module': instance.module,
                'entity_id': str(instance.entity_id),
                'state': instance.current_state.name,
                'comment': comment,
            },
        )

    @classmethod
    def _to_decimal(cls, value: Any, field_name: str) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception as exc:
            raise WorkflowEngineError(f'Invalid numeric value for {field_name}') from exc

    @classmethod
    def _apply_domain_transition(
        cls,
        module_code: str,
        entity,
        action: str,
        user: User,
        comment: str,
        payload: Dict[str, Any] | None,
    ):
        payload = payload or {}

        if module_code == WorkflowDefinition.Module.VARIATION:
            from apps.variations.services import VariationService

            if action == 'submit':
                return VariationService.submit_for_approval(str(entity.id), submitted_by=user)
            if action == 'approve':
                approved_value = payload.get('approved_value')
                return VariationService.approve_variation(
                    str(entity.id),
                    approved_by=user,
                    approved_value=cls._to_decimal(approved_value, 'approved_value') if approved_value is not None else None,
                    notes=payload.get('notes') or comment,
                )
            if action == 'reject':
                return VariationService.reject_variation(
                    str(entity.id),
                    rejected_by=user,
                    rejection_reason=payload.get('rejection_reason') or comment or 'Rejected',
                )
            if action == 'certify':
                certified_amount = payload.get('certified_amount')
                if certified_amount is None:
                    raise WorkflowEngineError('certified_amount is required for certify action')
                return VariationService.certify_variation(
                    str(entity.id),
                    certified_by=user,
                    certified_amount=cls._to_decimal(certified_amount, 'certified_amount'),
                    notes=payload.get('notes') or comment,
                )

        if module_code == WorkflowDefinition.Module.PROCUREMENT:
            from api.services.procurement_workflow import (
                approve_lpo,
                mark_lpo_delivered,
                mark_lpo_invoiced,
                mark_lpo_paid,
            )

            if action in {'submit', 'approve'}:
                approve_lpo(entity, approved_by=user)
                return entity.refresh_from_db() or entity
            if action == 'issue':
                entity.status = 'ISSUED'
                entity.save(update_fields=['status', 'updated_at'])
                return entity
            if action == 'deliver':
                mark_lpo_delivered(entity, delivered_by=user)
                return entity.refresh_from_db() or entity
            if action == 'invoice':
                mark_lpo_invoiced(entity, invoiced_by=user, invoice_number=payload.get('invoice_number'))
                return entity.refresh_from_db() or entity
            if action == 'pay':
                mark_lpo_paid(entity, paid_by=user, payment_reference=payload.get('payment_reference'))
                return entity.refresh_from_db() or entity

        if module_code == WorkflowDefinition.Module.CLAIM:
            from apps.subcontracts.services import SubcontractService

            if action == 'submit':
                if entity.status != 'DRAFT':
                    raise WorkflowEngineError('Only draft claims can be submitted')
                entity.status = 'SUBMITTED'
                entity.submitted_by = user
                entity.submitted_date = timezone.now()
                entity.save(update_fields=['status', 'submitted_by', 'submitted_date', 'updated_at'])
                return entity
            if action == 'certify':
                certified_amount = payload.get('certified_amount')
                if certified_amount is None:
                    raise WorkflowEngineError('certified_amount is required for certify action')
                return SubcontractService.certify_claim(
                    claim=entity,
                    certified_amount=cls._to_decimal(certified_amount, 'certified_amount'),
                    certified_by=user,
                    notes=payload.get('notes') or comment,
                )
            if action == 'reject':
                return SubcontractService.reject_claim(
                    claim=entity,
                    rejection_reason=payload.get('rejection_reason') or comment or 'Rejected',
                    rejected_by=user,
                )
            if action == 'pay':
                return SubcontractService.mark_claim_paid(
                    claim=entity,
                    paid_by=user,
                    payment_reference=payload.get('payment_reference', ''),
                )

        if module_code == WorkflowDefinition.Module.CONTRACT:
            from apps.subcontracts.services import SubcontractService

            if action == 'activate':
                return SubcontractService.activate_subcontract(subcontract=entity, activated_by=user)
            if action == 'complete':
                return SubcontractService.complete_subcontract(subcontract=entity, completed_by=user)
            if action == 'terminate':
                entity.status = 'TERMINATED'
                entity.completed_at = timezone.now()
                entity.save(update_fields=['status', 'completed_at', 'updated_at'])
                return entity

        raise WorkflowEngineError(f'Unsupported action "{action}" for module {module_code}')

    @classmethod
    @transaction.atomic
    def perform_transition(
        cls,
        user: User,
        module: str,
        entity_id: str,
        action: str,
        comment: str = '',
        payload: Dict[str, Any] | None = None,
    ) -> WorkflowInstance:
        module_code = cls.normalize_module(module)
        instance = cls.initialize_workflow(module=module_code, entity_id=entity_id, user=user)

        transition = WorkflowTransition.objects.filter(
            workflow=instance.workflow,
            from_state=instance.current_state,
            action=action,
        ).select_related('from_state', 'to_state').first()
        if not transition:
            raise WorkflowEngineError(
                f'Invalid transition action "{action}" from state "{instance.current_state.name}"'
            )

        user_roles = cls._get_user_roles(user)
        required_roles = {str(role).lower() for role in (transition.allowed_roles or [])}
        if required_roles and not user_roles.intersection(required_roles):
            raise WorkflowEngineError('You are not authorized to perform this transition')

        entity = cls._resolve_entity(module_code, entity_id)
        before_state = instance.current_state

        entity = cls._apply_domain_transition(
            module_code=module_code,
            entity=entity,
            action=action,
            user=user,
            comment=comment,
            payload=payload,
        )

        expected_state = transition.to_state
        instance.current_state = expected_state
        instance.last_transition_by = user
        instance.last_transition_at = timezone.now()

        instance.history = [
            *(instance.history or []),
            {
                'from': before_state.name,
                'to': expected_state.name,
                'action': action,
                'performed_by': str(user.id),
                'timestamp': instance.last_transition_at.isoformat(),
                'comment': comment,
            },
        ]
        instance.save(update_fields=['current_state', 'last_transition_by', 'last_transition_at', 'history', 'updated_at'])

        WorkflowHistory.objects.create(
            instance=instance,
            from_state=before_state,
            to_state=expected_state,
            action=action,
            performed_by=user,
            comment=comment,
        )

        project_id = cls._entity_project_id(entity)
        if project_id:
            activity_type_map = {
                'submit': ProjectActivity.ActivityType.APPROVAL_REQUESTED,
                'approve': ProjectActivity.ActivityType.APPROVAL_GRANTED,
                'certify': ProjectActivity.ActivityType.APPROVAL_GRANTED,
                'reject': ProjectActivity.ActivityType.APPROVAL_REJECTED,
                'issue': ProjectActivity.ActivityType.LPO_ISSUED,
                'deliver': ProjectActivity.ActivityType.LPO_DELIVERED,
                'invoice': ProjectActivity.ActivityType.LPO_ISSUED,
                'pay': ProjectActivity.ActivityType.SUPPLIER_PAYMENT,
                'activate': ProjectActivity.ActivityType.PROJECT_STARTED,
                'complete': ProjectActivity.ActivityType.PROJECT_COMPLETED,
                'terminate': ProjectActivity.ActivityType.APPROVAL_REJECTED,
            }
            log_activity(
                project_id=project_id,
                activity_type=activity_type_map.get(action, ProjectActivity.ActivityType.APPROVAL_REQUESTED),
                description=(
                    f'{instance.get_module_display()} {cls._entity_reference(module_code, entity)} '
                    f'transitioned from {before_state.name} to {expected_state.name} by {user.get_full_name() or user.username}'
                ),
                performed_by=user,
                related_object_type=instance.module,
                related_object_id=instance.entity_id,
                metadata={
                    'action': action,
                    'comment': comment,
                    'from_state': before_state.name,
                    'to_state': expected_state.name,
                },
            )

        cls._notify_transition(instance=instance, actor=user, action=action, comment=comment)

        return instance

    @classmethod
    def get_workflow_snapshot(cls, user: User, module: str, entity_id: str) -> Dict[str, Any]:
        instance = cls.initialize_workflow(module=module, entity_id=entity_id, user=user)
        available = cls.get_available_transitions(user=user, module=module, entity_id=entity_id)

        return {
            'instance_id': str(instance.id),
            'module': instance.module,
            'entity_id': str(instance.entity_id),
            'current_state': instance.current_state.name,
            'available_actions': [
                {
                    'action': transition.action,
                    'to_state': transition.to_state.name,
                    'allowed_roles': transition.allowed_roles or [],
                }
                for transition in available
            ],
            'history': [
                {
                    'id': str(item.id),
                    'from_state': item.from_state.name if item.from_state else None,
                    'to_state': item.to_state.name if item.to_state else None,
                    'action': item.action,
                    'performed_by': item.performed_by.get_full_name() if item.performed_by else None,
                    'performed_by_id': str(item.performed_by.id) if item.performed_by else None,
                    'timestamp': item.timestamp,
                    'comment': item.comment,
                }
                for item in instance.transition_history.select_related('from_state', 'to_state', 'performed_by').all()[:100]
            ],
            'last_transition_by': str(instance.last_transition_by_id) if instance.last_transition_by_id else None,
            'last_transition_at': instance.last_transition_at,
        }
