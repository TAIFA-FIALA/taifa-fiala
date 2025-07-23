import React from 'react';
import { Clock, MapPin, Users, Award, DollarSign, Calendar, Building, Target, AlertCircle, CheckCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface FundingAnnouncementBaseProps {
  id: string;
  title: string;
  organization: string;
  isActive: boolean;
  isOpen: boolean;
  sector: string;
  deadline?: string;
  country: string;
  region?: string;
  eligibilityCriteria: string[];
  detailsUrl: string;
  requiresRegistration: boolean;
  tags?: string[];
  currency?: string;
  
  // Enhanced financial information
  totalFundingPool?: number;
  fundingType: 'total_pool' | 'per_project_exact' | 'per_project_range';
  minAmountPerProject?: number;
  maxAmountPerProject?: number;
  exactAmountPerProject?: number;
  estimatedProjectCount?: number;
  projectCountRange?: { min: number; max: number };
  
  // Application & process information
  applicationProcess?: string;
  selectionCriteria?: string[];
  applicationDeadlineType?: 'rolling' | 'fixed' | 'multiple_rounds';
  announcementDate?: string;
  fundingStartDate?: string;
  projectDuration?: string;
  reportingRequirements?: string[];
  
  // Targeting & focus
  targetAudience?: string[];
  aiSubsectors?: string[];
  developmentStage?: string[];
  collaborationRequired?: boolean;
  genderFocused?: boolean;
  youthFocused?: boolean;
}

// Type definitions for the three funding patterns
interface TotalFundingProps extends FundingAnnouncementBaseProps {
  fundingType: 'total_pool';
  totalFundingPool: number;
  estimatedProjectCount?: number;
  projectCountRange?: { min: number; max: number };
}

interface ExactFundingProps extends FundingAnnouncementBaseProps {
  fundingType: 'per_project_exact';
  exactAmountPerProject: number;
}

interface RangeFundingProps extends FundingAnnouncementBaseProps {
  fundingType: 'per_project_range';
  minAmountPerProject: number;
  maxAmountPerProject: number;
}

type FundingAnnouncementCardProps = TotalFundingProps | ExactFundingProps | RangeFundingProps;

export function FundingAnnouncementCard(props: FundingAnnouncementCardProps) {
  const {
    id,
    title,
    organization,
    isActive,
    isOpen,
    sector,
    fundingType,
    currency = 'USD',
    deadline,
    country,
    region,
    eligibilityCriteria,
    detailsUrl,
    requiresRegistration,
    tags = [],
    applicationProcess,
    selectionCriteria = [],
    applicationDeadlineType,
    announcementDate,
    fundingStartDate,
    projectDuration,
    reportingRequirements = [],
    targetAudience = [],
    aiSubsectors = [],
    developmentStage = [],
    collaborationRequired,
    genderFocused,
    youthFocused,
  } = props;

  const formatCurrency = (amount: number) => 
    new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: currency,
      maximumFractionDigits: 0,
      notation: amount >= 1000000 ? 'compact' : 'standard'
    }).format(amount);

  const renderFundingAmount = () => {
    switch (fundingType) {
      case 'total_pool':
        const { totalFundingPool, estimatedProjectCount, projectCountRange } = props as TotalFundingProps;
        return (
          <div className="space-y-1">
            <span className="font-medium">{formatCurrency(totalFundingPool)} total pool</span>
            {estimatedProjectCount && (
              <div className="text-xs text-taifa-muted">
                ~{estimatedProjectCount} awards expected
              </div>
            )}
            {projectCountRange && (
              <div className="text-xs text-taifa-muted">
                {projectCountRange.min}-{projectCountRange.max} awards expected
              </div>
            )}
          </div>
        );
      case 'per_project_exact':
        const { exactAmountPerProject } = props as ExactFundingProps;
        return <span className="font-medium">{formatCurrency(exactAmountPerProject)} per project</span>;
      case 'per_project_range':
        const { minAmountPerProject, maxAmountPerProject } = props as RangeFundingProps;
        return (
          <span className="font-medium">
            {formatCurrency(minAmountPerProject)} - {formatCurrency(maxAmountPerProject)} per project
          </span>
        );
      default:
        return <span className="text-taifa-muted">Amount not specified</span>;
    }
  };

  const getDeadlineUrgency = () => {
    if (!deadline) return null;
    
    const deadlineDate = new Date(deadline);
    const today = new Date();
    const daysUntil = Math.ceil((deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysUntil < 0) return { level: 'expired', color: 'bg-gray-500', days: Math.abs(daysUntil) };
    if (daysUntil <= 7) return { level: 'urgent', color: 'bg-red-500', days: daysUntil };
    if (daysUntil <= 30) return { level: 'soon', color: 'bg-orange-500', days: daysUntil };
    return { level: 'normal', color: 'bg-green-500', days: daysUntil };
  };

  const deadlineInfo = getDeadlineUrgency();

  return (
    <div className="bg-white rounded-lg border border-taifa-border shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden h-full flex flex-col">
      {/* Header with status badges */}
      <div className="p-4 border-b border-taifa-border">
        <div className="flex justify-between items-start gap-2">
          <div className="flex-1">
            <h3 className="text-lg font-bold text-taifa-primary line-clamp-2">{title}</h3>
            <p className="text-sm text-taifa-muted mt-1 flex items-center">
              <Building className="h-3 w-3 mr-1" />
              {organization}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <Badge 
              variant={isActive ? 'default' : 'outline'} 
              className={`${isActive ? 'bg-taifa-accent text-white' : 'bg-taifa-light text-taifa-muted'}`}
            >
              {isActive ? 'Active' : 'Inactive'}
            </Badge>
            <Badge 
              variant={isOpen ? 'default' : 'outline'} 
              className={`${isOpen ? 'bg-taifa-secondary text-taifa-dark' : 'bg-taifa-light text-taifa-muted'}`}
            >
              {isOpen ? 'Open' : 'Closed'}
            </Badge>
            {deadlineInfo && (
              <Badge 
                variant="outline" 
                className={`text-white ${deadlineInfo.color} border-0`}
              >
                {deadlineInfo.level === 'expired' 
                  ? `Expired ${deadlineInfo.days}d ago`
                  : `${deadlineInfo.days}d left`
                }
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="p-4 flex-1 flex flex-col">
        {/* Sector and Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          <Badge className="bg-taifa-olive text-white">
            {sector}
          </Badge>
          {tags.map((tag, index) => (
            <Badge key={index} variant="outline" className="bg-taifa-light">
              {tag}
            </Badge>
          ))}
        </div>

        {/* Key details */}
        <div className="space-y-3 text-sm mb-4">
          {/* Funding Amount Display */}
          <div className="flex items-start">
            <DollarSign className="h-4 w-4 mr-2 text-taifa-accent flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-medium">Funding: </span>
              {renderFundingAmount()}
            </div>
          </div>
          
          <div className="flex items-center">
            <MapPin className="h-4 w-4 mr-2 text-taifa-red flex-shrink-0" />
            <span className="text-taifa-dark">
              {country}
              {region && `, ${region}`}
            </span>
          </div>
          
          {deadline && (
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-2 text-taifa-orange flex-shrink-0" />
              <div className="flex-1">
                <span className="font-medium">Deadline: </span>
                <span className="text-taifa-dark">{new Date(deadline).toLocaleDateString()}</span>
                {applicationDeadlineType && (
                  <span className="ml-2 text-xs text-taifa-muted">({applicationDeadlineType})</span>
                )}
              </div>
            </div>
          )}

          {projectDuration && (
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-2 text-taifa-secondary flex-shrink-0" />
              <span className="text-taifa-dark">
                <span className="font-medium">Duration: </span>
                {projectDuration}
              </span>
            </div>
          )}
        </div>

        {/* Focus Areas */}
        {(genderFocused || youthFocused || collaborationRequired) && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-taifa-primary mb-2 flex items-center">
              <Target className="h-4 w-4 mr-1" />
              Special Focus:
            </h4>
            <div className="flex flex-wrap gap-1">
              {genderFocused && (
                <Badge variant="outline" className="text-xs bg-pink-50 border-pink-200">
                  Women-focused
                </Badge>
              )}
              {youthFocused && (
                <Badge variant="outline" className="text-xs bg-blue-50 border-blue-200">
                  Youth-focused
                </Badge>
              )}
              {collaborationRequired && (
                <Badge variant="outline" className="text-xs bg-purple-50 border-purple-200">
                  Partnership required
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Target Audience */}
        {targetAudience.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-taifa-primary mb-2 flex items-center">
              <Users className="h-4 w-4 mr-1" />
              Target Audience:
            </h4>
            <div className="flex flex-wrap gap-1">
              {targetAudience.slice(0, 3).map((audience, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {audience}
                </Badge>
              ))}
              {targetAudience.length > 3 && (
                <Badge variant="outline" className="text-xs text-taifa-muted">
                  +{targetAudience.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* AI Subsectors */}
        {aiSubsectors.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-taifa-primary mb-2">
              AI Focus Areas:
            </h4>
            <div className="flex flex-wrap gap-1">
              {aiSubsectors.slice(0, 3).map((subsector, index) => (
                <Badge key={index} variant="outline" className="text-xs bg-blue-50 border-blue-200">
                  {subsector}
                </Badge>
              ))}
              {aiSubsectors.length > 3 && (
                <Badge variant="outline" className="text-xs text-taifa-muted">
                  +{aiSubsectors.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Eligibility Criteria */}
        {eligibilityCriteria.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-taifa-primary mb-2 flex items-center">
              <CheckCircle className="h-4 w-4 mr-1" />
              Key Requirements:
            </h4>
            <ul className="list-disc list-inside text-sm space-y-1 text-taifa-muted">
              {eligibilityCriteria.slice(0, 3).map((criteria, index) => (
                <li key={index} className="line-clamp-1">
                  {criteria}
                </li>
              ))}
              {eligibilityCriteria.length > 3 && (
                <li className="text-taifa-accent cursor-pointer hover:underline">
                  +{eligibilityCriteria.length - 3} more requirements...
                </li>
              )}
            </ul>
          </div>
        )}

        {/* Application Process Preview */}
        {applicationProcess && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-taifa-primary mb-2">
              Application Process:
            </h4>
            <p className="text-sm text-taifa-muted line-clamp-2">
              {applicationProcess}
            </p>
          </div>
        )}

        {/* Reporting Requirements */}
        {reportingRequirements.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-taifa-primary mb-2 flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              Reporting Required:
            </h4>
            <div className="flex flex-wrap gap-1">
              {reportingRequirements.slice(0, 2).map((requirement, index) => (
                <Badge key={index} variant="outline" className="text-xs bg-yellow-50 border-yellow-200">
                  {requirement}
                </Badge>
              ))}
              {reportingRequirements.length > 2 && (
                <Badge variant="outline" className="text-xs text-taifa-muted">
                  +{reportingRequirements.length - 2} more
                </Badge>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer with actions */}
      <div className="p-4 border-t border-taifa-border bg-taifa-light/30">
        <div className="flex justify-between items-center">
          <a
            href={detailsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-taifa-accent hover:underline flex items-center"
          >
            View Full Details
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 ml-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </a>
          
          {isOpen && (
            <Button 
              size="sm" 
              className="bg-taifa-secondary hover:bg-taifa-orange text-taifa-dark font-medium"
              onClick={() => console.log('Apply clicked:', id)}
            >
              {requiresRegistration ? 'Register to Apply' : 'Apply Now'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}