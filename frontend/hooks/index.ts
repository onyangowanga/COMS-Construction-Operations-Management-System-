// ============================================================================
// HOOKS - CENTRAL EXPORT
// Export all hooks from a single entry point
// ============================================================================

export { useAuth } from './useAuth';
export { usePermissions } from './usePermissions';
export { useToast } from './useToast';
export { useApi } from './useApi';
export { useProjects, useProject, useProjectDashboard, useProjectMetrics, useProjectStages } from './useProjects';
export { useNotifications } from './useNotifications';
export { useDocuments, useDocument } from './useDocuments';
export { useVariations, useVariation } from './useVariations';
export { useClaims, useClaim } from './useClaims';
export { useProcurement, useProcurementOrder } from './useProcurement';
export { useSubcontractors, useSubcontractor } from './useSubcontractors';
export { useSuppliers, useSupplier } from './useSuppliers';
export { useContracts, useContract } from './useContracts';
export { useActivity, useActivityItem } from './useActivity';
export {
	useReports,
	useReport,
	useReportExecutions,
	useReportExecutionProgress,
	useReportSchedules,
	useDashboardWidgets,
} from './useReports';
