'use client';

import { useSearchParams } from 'next/navigation';

export interface DrilldownContext {
  /** Pre-seeded search term when navigating from a dashboard widget (URL ?search=...) */
  search: string;
  /** Pre-seeded status filter when navigating from a dashboard widget (URL ?status=...) */
  status: string;
  /** The originating report ID, present when navigating from a dashboard widget */
  reportId: string | null;
  /** True when this page was reached via a dashboard widget drill-down */
  isDrilldown: boolean;
}

/**
 * Reads drill-down context from the current URL search params.
 * Module list pages use the returned values to initialise filter state so
 * that navigating here from a dashboard widget opens an already-filtered view.
 *
 * The DashboardWidgetGrid pushes URLs like:
 *   /procurement?report_id=<uuid>&status=APPROVED&search=...
 */
export function useDrilldownFilter(): DrilldownContext {
  const searchParams = useSearchParams();

  return {
    search: searchParams.get('search') ?? '',
    status: searchParams.get('status') ?? '',
    reportId: searchParams.get('report_id'),
    isDrilldown: searchParams.has('report_id'),
  };
}
