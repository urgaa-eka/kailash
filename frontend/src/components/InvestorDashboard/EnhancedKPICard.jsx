import React from 'react';
import DataSourceBadge from './DataSourceBadge';

/**
 * EnhancedKPICard - KPI card with data provenance
 * Uses existing graphite card pattern with electric yellow for values
 */
const EnhancedKPICard = ({ 
  title, 
  value, 
  source, 
  type, 
  timestamp,
  trend,
  trendDirection = 'up',
  aiCalculated,
  description,
  icon
}) => {
  return (
    <div className="bg-g4g-graphite rounded-lg p-4 border border-g4g-steel-grey hover:border-g4g-electric-yellow/50 transition-all duration-200">
      {/* Header with title and data source */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          {icon && (
            <span className="text-g4g-electric-yellow">
              {icon}
            </span>
          )}
          <span className="text-sm text-cool-grey font-medium">{title}</span>
        </div>
        <DataSourceBadge source={source} type={type} timestamp={timestamp} />
      </div>
      
      {/* Value */}
      <div className="text-3xl font-black text-g4g-electric-yellow mb-2">
        {value}
      </div>
      
      {/* Trend and Description */}
      <div className="flex items-center justify-between">
        {trend && (
          <span className={`text-xs font-semibold flex items-center gap-1 ${trendDirection === 'up' ? 'text-highlight-teal' : trendDirection === 'down' ? 'text-error-red' : 'text-cool-grey'}`}>
            {trendDirection === 'up' && (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 15l-6-6-6 6"/>
              </svg>
            )}
            {trendDirection === 'down' && (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 9l6 6 6-6"/>
              </svg>
            )}
            {trend}
          </span>
        )}
        {description && (
          <span className="text-xs text-cool-grey">{description}</span>
        )}
      </div>
      
      {/* AI Calculated indicator */}
      {aiCalculated && (
        <div className="mt-2 pt-2 border-t border-g4g-steel-grey/50">
          <span className="text-[10px] text-highlight-teal flex items-center gap-1">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6M12 17v6M4.22 4.22l4.24 4.24M15.54 15.54l4.24 4.24M1 12h6M17 12h6"/>
            </svg>
            AI-calculated from real-time data
          </span>
        </div>
      )}
    </div>
  );
};

export default EnhancedKPICard;
