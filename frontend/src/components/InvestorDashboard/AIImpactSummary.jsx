import React from 'react';
import DataSourceBadge from './DataSourceBadge';

/**
 * AIImpactSummary - Top-level metrics showing AI value
 * Uses existing KPI card styling with electric yellow for values
 */
const AIImpactSummary = ({ metrics }) => {
  const defaultMetrics = {
    problemsResolved: 47,
    automationRate: 92,
    humanIntervention: 8,
    dataPointsProcessed: 12847,
    avgResolutionTime: '4.2 min',
    manualTime: '45 min',
    platforms: {
      URGAA: { dataPoints: 7234, problems: 23 },
      GSTSAAS: { dataPoints: 4126, problems: 18 },
      IGNITION: { dataPoints: 1487, problems: 6 }
    }
  };

  const data = { ...defaultMetrics, ...metrics };

  return (
    <div className="mb-8">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-g4g-electric-yellow">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
          AI Impact Today
        </h2>
        <span className="text-xs text-highlight-teal font-medium px-2 py-1 bg-highlight-teal/10 rounded-full">
          Live
        </span>
      </div>

      {/* Impact Cards Grid */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {/* Problems Resolved */}
        <div className="bg-g4g-graphite rounded-xl p-5 border border-g4g-steel-grey hover:border-g4g-electric-yellow/50 transition-all">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs text-cool-grey font-medium">Problems Resolved</span>
            <span className="text-[10px] text-highlight-teal bg-highlight-teal/10 px-1.5 py-0.5 rounded">+23%</span>
          </div>
          <div className="text-4xl font-black text-g4g-electric-yellow mb-1">{data.problemsResolved}</div>
          <div className="text-xs text-cool-grey">across all platforms</div>
        </div>

        {/* Automation Rate */}
        <div className="bg-g4g-graphite rounded-xl p-5 border border-g4g-steel-grey hover:border-g4g-electric-yellow/50 transition-all">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs text-cool-grey font-medium">Fully Automated</span>
            <span className="text-[10px] text-highlight-teal bg-highlight-teal/10 px-1.5 py-0.5 rounded">-3% manual</span>
          </div>
          <div className="text-4xl font-black text-g4g-electric-yellow mb-1">{data.automationRate}%</div>
          <div className="text-xs text-cool-grey">
            <span className="text-highlight-teal">{data.humanIntervention}%</span> required human help
          </div>
        </div>

        {/* Data Points Processed */}
        <div className="bg-g4g-graphite rounded-xl p-5 border border-g4g-steel-grey hover:border-g4g-electric-yellow/50 transition-all">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs text-cool-grey font-medium">Data Points</span>
            <span className="text-[10px] text-cool-grey">3 platforms</span>
          </div>
          <div className="text-4xl font-black text-g4g-electric-yellow mb-2">{data.dataPointsProcessed.toLocaleString()}</div>
          <div className="flex gap-2">
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">URGAA {(data.platforms?.URGAA?.dataPoints || 7234).toLocaleString()}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400">GST {(data.platforms?.GSTSAAS?.dataPoints || 4126).toLocaleString()}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-pink-500/20 text-pink-400">IGN {(data.platforms?.IGNITION?.dataPoints || 1487).toLocaleString()}</span>
          </div>
        </div>

        {/* Resolution Time */}
        <div className="bg-g4g-graphite rounded-xl p-5 border border-g4g-steel-grey hover:border-g4g-electric-yellow/50 transition-all">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs text-cool-grey font-medium">Avg Resolution</span>
            <span className="text-[10px] text-highlight-teal bg-highlight-teal/10 px-1.5 py-0.5 rounded">91% faster</span>
          </div>
          <div className="text-4xl font-black text-g4g-electric-yellow mb-1">{data.avgResolutionTime}</div>
          <div className="text-xs text-cool-grey">vs <span className="text-error-red">{data.manualTime}</span> manual</div>
        </div>
      </div>

      {/* Platform Breakdown */}
      <div className="bg-g4g-graphite/50 rounded-lg p-4 border border-g4g-steel-grey/50">
        <div className="flex items-center justify-between">
          <span className="text-xs text-cool-grey font-medium">Problems by Platform:</span>
          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <DataSourceBadge source="URGAA" />
              <span className="text-sm font-semibold text-white">{data.platforms?.URGAA?.problems || 23} solved</span>
            </div>
            <div className="flex items-center gap-2">
              <DataSourceBadge source="GSTSAAS" />
              <span className="text-sm font-semibold text-white">{data.platforms?.GSTSAAS?.problems || 18} solved</span>
            </div>
            <div className="flex items-center gap-2">
              <DataSourceBadge source="IGNITION" />
              <span className="text-sm font-semibold text-white">{data.platforms?.IGNITION?.problems || 6} solved</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIImpactSummary;
