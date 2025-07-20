"use client";

import { useState } from 'react';
import {
  Calendar, DollarSign, MapPin, Building, ExternalLink, Clock,
  Users, TrendingUp, Award, ChevronDown, ChevronUp,
  Globe, Brain, Shield, AlertCircle, UserCheck, GraduationCap, Home
} from 'lucide-react';
import { FundingOpportunity } from '@/types/funding';

interface OpportunityCardProps {
  opportunity: FundingOpportunity;
  searchMode: 'discover' | 'explore';
  onViewDetails?: (id: number) => void;
}

export default function OpportunityCard({ opportunity, searchMode }: OpportunityCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showEquityDetails, setShowEquityDetails] = useState(false);

  const formatAmount = (amount?: number, currency = 'USD') => {
    if (!amount) return null;
    
    if (amount >= 1e6) {
      return `${(amount / 1e6).toFixed(1)}M ${currency}`;
    } else if (amount >= 1e3) {
      return `${(amount / 1e3).toFixed(0)}K ${currency}`;
    } else {
      return `${amount.toLocaleString()} ${currency}`;
    }
  };

  const getFundingAmountDisplay = () => {
    if (opportunity.amount_exact) {
      return formatAmount(opportunity.amount_exact, opportunity.currency);
    } else if (opportunity.amount_min && opportunity.amount_max) {
      return `${formatAmount(opportunity.amount_min, opportunity.currency)} - ${formatAmount(opportunity.amount_max, opportunity.currency)}`;
    } else if (opportunity.amount_min) {
      return `${formatAmount(opportunity.amount_min, opportunity.currency)}+`;
    } else if (opportunity.amount_max) {
      return `Up to ${formatAmount(opportunity.amount_max, opportunity.currency)}`;
    }
    return 'Amount not specified';
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'open':
        return 'bg-[#F0E68C] bg-opacity-30 text-[#1F2A44]';
      case 'closed':
        return 'bg-[#A0A0A0] bg-opacity-30 text-[#1F2A44]';
      case 'awarded':
        return 'bg-[#4B9CD3] bg-opacity-30 text-[#1F2A44]';
      case 'cancelled':
        return 'bg-[#A0A0A0] bg-opacity-30 text-[#1F2A44]';
      default:
        return 'bg-[#F0E68C] bg-opacity-20 text-[#1F2A44]';
    }
  };

  const getEquityScore = () => {
    if (!opportunity.equity_score) return null;
    
    const score = opportunity.equity_score;
    let color = 'text-[#1F2A44]';
    let bgColor = 'bg-[#A0A0A0] bg-opacity-20';
    
    if (score >= 80) {
      color = 'text-[#1F2A44]';
      bgColor = 'bg-[#4B9CD3] bg-opacity-30';
    } else if (score >= 60) {
      color = 'text-[#1F2A44]';
      bgColor = 'bg-[#4B9CD3] bg-opacity-20';
    } else if (score >= 40) {
      color = 'text-[#1F2A44]';
      bgColor = 'bg-[#F0E68C] bg-opacity-30';
    } else {
      color = 'text-[#1F2A44]';
      bgColor = 'bg-[#A0A0A0] bg-opacity-30';
    }
    
    return { score, color, bgColor };
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getDaysUntilDeadline = () => {
    if (!opportunity.deadline) return null;
    
    const deadline = new Date(opportunity.deadline);
    const today = new Date();
    const diffTime = deadline.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
  };

  const daysUntilDeadline = getDaysUntilDeadline();
  const equityScore = getEquityScore();

  return (
    <div className="bg-white rounded-xl shadow-lg border border-[#A0A0A0] border-opacity-20 hover:shadow-xl transition-shadow duration-300 overflow-hidden">
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-[#1F2A44] mb-2 line-clamp-2">
              {opportunity.title}
            </h3>
            
            <div className="flex items-center space-x-4 mb-3">
              {/* Status Badge */}
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(opportunity.status)}`}>
                {opportunity.status}
              </span>
              
              {/* Funding Type */}
              {opportunity.funding_type && (
                <span className="px-3 py-1 bg-[#4B9CD3] bg-opacity-20 text-[#1F2A44] rounded-full text-xs font-medium">
                  {opportunity.funding_type.name}
                </span>
              )}
              
              {/* Equity Score */}
              {equityScore && (
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${equityScore.bgColor} ${equityScore.color}`}>
                  Equity Score: {equityScore.score}
                </span>
              )}
            </div>
          </div>
          
          {/* Deadline Alert */}
          {daysUntilDeadline && daysUntilDeadline <= 30 && (
            <div className={`ml-4 px-3 py-1 rounded-full text-xs font-medium ${
              daysUntilDeadline <= 7 ? 'bg-[#A0A0A0] bg-opacity-40 text-[#1F2A44]' : 'bg-[#F0E68C] bg-opacity-30 text-[#1F2A44]'
            }`}>
              {daysUntilDeadline <= 0 ? 'Deadline passed' : `${daysUntilDeadline} days left`}
            </div>
          )}
        </div>

        {/* Key Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* Funding Amount */}
          <div className="flex items-center space-x-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            <div>
              <div className="text-lg font-semibold text-green-600">
                {getFundingAmountDisplay()}
              </div>
              {opportunity.funding_type?.requires_equity && (
                <div className="text-xs text-gray-500">
                  {opportunity.investment_specific?.equity_percentage && 
                    `${opportunity.investment_specific.equity_percentage}% equity required`
                  }
                </div>
              )}
            </div>
          </div>

          {/* Deadline */}
          {opportunity.deadline && (
            <div className="flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              <div>
                <div className="text-sm font-medium text-gray-900">
                  {formatDate(opportunity.deadline)}
                </div>
                <div className="text-xs text-gray-500">Application deadline</div>
              </div>
            </div>
          )}
        </div>

        {/* Organization */}
        {opportunity.provider_organization && (
          <div className="flex items-center space-x-2 mb-4">
            <Building className="w-5 h-5 text-purple-600" />
            <div>
              <div className="text-sm font-medium text-gray-900">
                {opportunity.provider_organization.name}
              </div>
              <div className="text-xs text-gray-500">
                {opportunity.provider_organization.type}
                {opportunity.provider_organization.country && 
                  ` • ${opportunity.provider_organization.country}`
                }
              </div>
            </div>
          </div>
        )}

        {/* Description */}
        <p className="text-gray-600 text-sm line-clamp-3 mb-4">
          {opportunity.description}
        </p>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {/* AI Domains */}
          {opportunity.ai_domains?.slice(0, 3).map((domain) => (
            <span key={domain.id} className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs">
              {domain.name}
            </span>
          ))}
          
          {/* Geographic Scope */}
          {opportunity.geographic_scope_names?.slice(0, 2).map((scope) => (
            <span key={scope} className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs flex items-center space-x-1">
              <Globe className="w-3 h-3" />
              <span>{scope}</span>
            </span>
          ))}
          
          {/* Inclusion Indicators */}
          {opportunity.inclusion_indicators?.slice(0, 2).map((indicator) => (
            <span key={indicator} className="px-2 py-1 bg-pink-100 text-pink-800 rounded-full text-xs flex items-center space-x-1">
              <Users className="w-3 h-3" />
              <span>{indicator}</span>
            </span>
          ))}
        </div>

        {/* Equity Focus Indicators */}
        {(opportunity.underserved_focus || opportunity.women_focus || opportunity.youth_focus || opportunity.rural_focus) && (
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="w-4 h-4 text-blue-600" />
            <div className="flex space-x-2">
              {opportunity.underserved_focus && (
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded flex items-center space-x-1">
                  <Globe className="w-3 h-3" />
                  <span>Underserved Focus</span>
                </span>
              )}
              {opportunity.women_focus && (
                <span className="text-xs bg-pink-100 text-pink-800 px-2 py-1 rounded flex items-center space-x-1">
                  <UserCheck className="w-3 h-3" />
                  <span>Women-Led</span>
                </span>
              )}
              {opportunity.youth_focus && (
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded flex items-center space-x-1">
                  <GraduationCap className="w-3 h-3" />
                  <span>Youth-Focused</span>
                </span>
              )}
              {opportunity.rural_focus && (
                <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded flex items-center space-x-1">
                  <Home className="w-3 h-3" />
                  <span>Rural</span>
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Expandable Details */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-4">
              {/* Grant-specific details */}
              {opportunity.grant_specific && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <Award className="w-4 h-4" />
                    <span>Grant Details</span>
                  </h4>
                  <div className="space-y-2 text-sm">
                    {opportunity.grant_specific.duration_months && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Duration:</span>
                        <span className="font-medium">{opportunity.grant_specific.duration_months} months</span>
                      </div>
                    )}
                    {opportunity.grant_specific.renewable !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Renewable:</span>
                        <span className="font-medium">{opportunity.grant_specific.renewable ? 'Yes' : 'No'}</span>
                      </div>
                    )}
                    {opportunity.grant_specific.project_based !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Project-based:</span>
                        <span className="font-medium">{opportunity.grant_specific.project_based ? 'Yes' : 'No'}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Investment-specific details */}
              {opportunity.investment_specific && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4" />
                    <span>Investment Details</span>
                  </h4>
                  <div className="space-y-2 text-sm">
                    {opportunity.investment_specific.equity_percentage && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Equity Required:</span>
                        <span className="font-medium">{opportunity.investment_specific.equity_percentage}%</span>
                      </div>
                    )}
                    {opportunity.investment_specific.valuation_cap && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Valuation Cap:</span>
                        <span className="font-medium">{formatAmount(opportunity.investment_specific.valuation_cap)}</span>
                      </div>
                    )}
                    {opportunity.investment_specific.expected_roi && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Expected ROI:</span>
                        <span className="font-medium">{opportunity.investment_specific.expected_roi}%</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Timeline */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <span>Timeline</span>
                </h4>
                <div className="space-y-2 text-sm">
                  {opportunity.announcement_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Announced:</span>
                      <span className="font-medium">{formatDate(opportunity.announcement_date)}</span>
                    </div>
                  )}
                  {opportunity.start_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Start Date:</span>
                      <span className="font-medium">{formatDate(opportunity.start_date)}</span>
                    </div>
                  )}
                  {opportunity.deadline && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Deadline:</span>
                      <span className="font-medium">{formatDate(opportunity.deadline)}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              {/* All AI Domains */}
              {opportunity.ai_domains && opportunity.ai_domains.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <Brain className="w-4 h-4" />
                    <span>AI Domains</span>
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {opportunity.ai_domains.map((domain) => (
                      <span key={domain.id} className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs">
                        {domain.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Geographic Coverage */}
              {opportunity.geographic_scope_names && opportunity.geographic_scope_names.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <MapPin className="w-4 h-4" />
                    <span>Geographic Coverage</span>
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {opportunity.geographic_scope_names.map((scope) => (
                      <span key={scope} className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                        {scope}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Bias Flags */}
              {opportunity.bias_flags && opportunity.bias_flags.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-yellow-600" />
                    <span>Bias Analysis</span>
                  </h4>
                  <div className="space-y-1">
                    {opportunity.bias_flags.map((flag: string, index: number) => (
                      <div key={index} className="text-xs text-yellow-700 bg-yellow-50 px-2 py-1 rounded">
                        {flag}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Metadata */}
              {searchMode === 'explore' && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Metadata</h4>
                  <div className="space-y-1 text-xs text-gray-600">
                    {opportunity.created_at && (
                      <div>Added: {formatDate(opportunity.created_at)}</div>
                    )}
                    {opportunity.last_checked && (
                      <div>Last checked: {formatDate(opportunity.last_checked)}</div>
                    )}
                    {opportunity.confidence_score && (
                      <div>Confidence: {(opportunity.confidence_score * 100).toFixed(0)}%</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              <span>{isExpanded ? 'Less Details' : 'More Details'}</span>
            </button>
            
            {equityScore && (
              <button
                onClick={() => setShowEquityDetails(!showEquityDetails)}
                className="flex items-center space-x-2 text-purple-600 hover:text-purple-800 text-sm font-medium"
              >
                <Shield className="w-4 h-4" />
                <span>Equity Analysis</span>
              </button>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            {opportunity.application_url && (
              <a
                href={opportunity.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
              >
                <span>Apply Now</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
            
            {opportunity.source_url && (
              <a
                href={opportunity.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
              >
                <span>View Source</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}