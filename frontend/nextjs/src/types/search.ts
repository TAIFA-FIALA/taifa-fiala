import { FundingOpportunity } from './funding';

// Types for search functionality
export interface SearchFilters {
  query: string;
  min_amount: number;
  max_amount: number;
  amount_exact: number;
  deadline_after: string;
  deadline_before: string;
  status: string;
  funding_type: string;
  geographic_scope: string[];
  target_audience: string[];
  focus_areas: string[];
  sort_by: 'relevance' | 'deadline' | 'amount' | 'date_added';
  sort_order: 'asc' | 'desc';
  page: number;
  page_size: number;
  opportunity_type?: string;
  organization_type?: string;
  underserved_focus?: boolean;
  women_focus?: boolean;
  youth_focus?: boolean;
  rural_focus?: boolean;
  // Add any additional filter fields as needed
}

export type SearchMode = 'discover' | 'explore';

export interface SearchResultsProps {
  searchMode: SearchMode;
  filters: SearchFilters;
  loading: boolean;
  onLoadMore?: () => void;
}

export interface SearchResultsState {
  opportunities: FundingOpportunity[];
  total: number;
  currentPage: number;
  totalPages: number;
  perPage: number;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  viewMode: 'grid' | 'list';
  selectedFilters: string[];
}
