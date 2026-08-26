import React from 'react';

/**
 * DataSourceBadge - Shows data provenance for every metric
 * Uses existing Tailwind colors from tailwind.config.js
 */
const DataSourceBadge = ({ source, type, timestamp }) => {
  const sourceColors = {
    URGAA: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    GSTSAAS: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    IGNITION: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
    INTERNAL: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    ALL: 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  };

  const typeColors = {
    internal: 'bg-indigo-500/20 text-indigo-400',
    external: 'bg-emerald-500/20 text-emerald-400',
    INT: 'bg-indigo-500/20 text-indigo-400',
    EXT: 'bg-emerald-500/20 text-emerald-400'
  };

  return (
    <div className="inline-flex items-center gap-1.5">
      {/* Source Badge */}
      <span 
        className={`px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wide border ${sourceColors[source] || sourceColors.INTERNAL}`}
      >
        {source}
      </span>
      
      {/* Internal/External Badge */}
      {type && (
        <span 
          className={`px-1.5 py-0.5 rounded-md text-[10px] font-medium ${typeColors[type] || typeColors.internal}`}
        >
          {type === 'internal' ? 'INT' : type === 'external' ? 'EXT' : type}
        </span>
      )}
      
      {/* Timestamp */}
      {timestamp && (
        <span className="text-[10px] text-cool-grey ml-1">
          {timestamp}
        </span>
      )}
    </div>
  );
};

export default DataSourceBadge;
