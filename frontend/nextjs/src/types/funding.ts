export interface FundingOpportunity {
  id: number;
  title: string;
  description: string;
  
  // Funding amounts
  amount_min?: number;
  amount_max?: number;
  amount_exact?: number;
  amount_usd?: number;
  currency: string;
  
  // Timing
  deadline?: string;
  announcement_date?: string;
  start_date?: string;
  status: string;
  
  // Organization
  organization_id?: number;
  provider_organization?: {
    id: number;
    name: string;
    type: string;
    country?: string;
    website?: string;
    is_granting_agency?: boolean;
    is_venture_capital?: boolean;
  };
  
  // Classification
  funding_type?: {
    id: number;
    name: string;
    category: string;
    requires_equity?: boolean;
    requires_repayment?: boolean;
  };
  
  // Contact and links
  link?: string;
  contact_email?: string;
  application_url?: string;
  
  // Categories and domains
  categories?: string;
  ai_domains?: Array<{
    id: number;
    name: string;
    description?: string;
  }>;
  
  // Geographic
  geographical_scope?: string;
  geographic_scope_names?: string[];
  
  // Equity-aware metadata
  equity_score?: number;
  gender_inclusive?: boolean;
  supports_underrepresented?: boolean;
  inclusion_indicators?: string[];
  underserved_focus?: boolean;
  women_focus?: boolean;
  youth_focus?: boolean;
  rural_focus?: boolean;
  
  // Investment-specific properties
  investment_specific?: {
    equity_percentage?: number;
    valuation_cap?: number;
    interest_rate?: number;
    expected_roi?: number;
  };
  
  // Grant-specific properties
  grant_specific?: {
    reporting_requirements?: string;
    duration_months?: number;
    renewable?: boolean;
    project_based?: boolean;
  };
  
  // Data quality and tracking
  bias_flags?: string[];
  created_at?: string;
  last_checked?: string;
  confidence_score?: number;
  source_url?: string;
  
  // Additional metadata
  eligibility_criteria?: string;
  application_process?: string;
  selection_criteria?: string;
}

export interface AfricaIntelligenceItem {
  id: number;
  title: string;
  description: string;
  
  // Funding details
  amount_min?: number;
  amount_max?: number;
  amount_exact?: number;
  currency: string;
  amount_usd?: number;
  
  // Timing
  deadline?: string;
  announcement_date?: string;
  start_date?: string;
  status: string;
  
  // Organization
  provider_organization?: {
    id: number;
    name: string;
    type: string;
    country?: string;
    website?: string;
    is_granting_agency: boolean;
    is_venture_capital: boolean;
  };
  
  // Classification
  funding_type?: {
    id: number;
    name: string;
    category: string;
    requires_equity: boolean;
    requires_repayment: boolean;
  };
  
  ai_domains?: Array<{
    id: number;
    name: string;
    description?: string;
  }>;
  
  // Geographic
  geographical_scope?: string;
  geographic_scope_names?: string[];
  
  // Equity-aware metadata
  equity_score?: number;
  bias_flags?: string[];
  underserved_focus?: boolean;
  women_focus?: boolean;
  youth_focus?: boolean;
  rural_focus?: boolean;
  inclusion_indicators?: string[];
  
  // Type-specific data
  is_grant?: boolean;
  is_investment?: boolean;
  funding_category?: string;
  
  // Grant-specific
  grant_specific?: {
    reporting_requirements?: string;
    grant_duration_months?: number;
    renewable?: boolean;
    project_based?: boolean;
  };
  
  // Investment-specific
  investment_specific?: {
    equity_percentage?: number;
    valuation_cap?: number;
    expected_roi?: number;
    post_investment_support?: string;
  };
  
  // URLs
  source_url?: string;
  application_url?: string;
  contact_info?: string;
  
  // Meta
  created_at?: string;
  last_checked?: string;
  confidence_score?: number;
}