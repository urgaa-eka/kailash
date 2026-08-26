import React from 'react';
import DataSourceBadge from './DataSourceBadge';
import AutomationBadge from './AutomationBadge';

/**
 * ProblemResolutionCard - Shows problems being solved with data provenance
 * Uses graphite card pattern from existing design system
 */
const ProblemResolutionCard = ({ 
  problem, 
  solution, 
  source, 
  type, 
  automated, 
  timestamp,
  savings,
  compact = false 
}) => {
  if (compact) {
    return (
      <div className="bg-g4g-graphite rounded-lg p-3 border border-g4g-steel-grey hover:border-g4g-electric-yellow/30 transition-all">
        <div className="flex items-start justify-between gap-2 mb-2">
          <span className="text-error-red text-xs font-medium">Issue:</span>
          <DataSourceBadge source={source} type={type} timestamp={timestamp} />
        </div>
        <p className="text-white text-sm mb-2">{problem}</p>
        <div className="flex items-center justify-between">
          <span className="text-highlight-teal text-xs">Resolved</span>
          <AutomationBadge automated={automated} showLabel={false} />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-g4g-graphite rounded-lg p-4 border border-g4g-steel-grey hover:border-g4g-electric-yellow/30 transition-all duration-200">
      {/* Problem Header */}
      <div className="flex justify-between items-start mb-2">
        <span className="text-error-red font-semibold text-sm">Problem:</span>
        <DataSourceBadge source={source} type={type} timestamp={timestamp} />
      </div>
      <p className="text-white text-sm mb-4">{problem}</p>
      
      {/* Solution Header */}
      <div className="flex justify-between items-start mb-2">
        <span className="text-highlight-teal font-semibold text-sm">Solution:</span>
        <AutomationBadge automated={automated} />
      </div>
      <p className="text-cool-grey text-sm mb-3">{solution}</p>
      
      {/* Savings if provided */}
      {savings && (
        <div className="pt-3 border-t border-g4g-steel-grey">
          <span className="text-g4g-electric-yellow text-xs font-medium">
            Value: {savings}
          </span>
        </div>
      )}
      
      {/* Automated indicator */}
      {automated && (
        <div className="mt-3 pt-3 border-t border-g4g-steel-grey">
          <span className="text-g4g-electric-yellow text-xs flex items-center gap-1">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 6L7.5 14.5L4 11"/>
            </svg>
            No human intervention required
          </span>
        </div>
      )}
    </div>
  );
};

export default ProblemResolutionCard;
