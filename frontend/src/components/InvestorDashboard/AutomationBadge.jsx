import React from 'react';

/**
 * AutomationBadge - Shows whether task was AI-handled or manual
 * Uses existing design patterns with highlight-teal for automated
 */
const AutomationBadge = ({ automated, showLabel = true }) => {
  if (automated) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-semibold bg-highlight-teal/20 text-highlight-teal border border-highlight-teal/30">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="8"/>
          <path d="M12 8v4l2 2"/>
          <path d="M8 4l-2-2"/>
          <path d="M16 4l2-2"/>
        </svg>
        {showLabel && <span>AI Auto</span>}
      </span>
    );
  }
  
  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-semibold bg-cool-grey/20 text-cool-grey border border-cool-grey/30">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="6" r="4"/>
        <path d="M4 20c0-4.42 3.58-8 8-8s8 3.58 8 8"/>
      </svg>
      {showLabel && <span>Manual</span>}
    </span>
  );
};

export default AutomationBadge;
