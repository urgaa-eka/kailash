import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

/**
 * Square KPI Card Component
 * Colorful, compact KPI cards that reduce scrolling
 * 
 * @param {string} label - KPI label
 * @param {string|number} value - KPI value
 * @param {string} change - Change percentage (e.g., "+12%")
 * @param {boolean} isPositive - Whether change is positive
 * @param {React.Component} icon - Lucide icon component
 * @param {string} color - Color theme: 'blue', 'green', 'orange', 'purple', 'cyan', 'red'
 * @param {string} className - Additional CSS classes
 */

const COLOR_THEMES = {
  blue: {
    bg: 'bg-g4g-blue',
    bgLight: 'bg-g4g-blue/10',
    text: 'text-g4g-blue',
    gradient: 'from-g4g-blue to-blue-700'
  },
  green: {
    bg: 'bg-emerald-500',
    bgLight: 'bg-emerald-500/10',
    text: 'text-emerald-600',
    gradient: 'from-emerald-500 to-green-600'
  },
  orange: {
    bg: 'bg-g4g-electric-yellow',
    bgLight: 'bg-g4g-electric-yellow/10',
    text: 'text-amber-600',
    gradient: 'from-amber-500 to-orange-500'
  },
  purple: {
    bg: 'bg-purple-500',
    bgLight: 'bg-purple-500/10',
    text: 'text-purple-600',
    gradient: 'from-purple-500 to-indigo-600'
  },
  cyan: {
    bg: 'bg-cyan-500',
    bgLight: 'bg-cyan-500/10',
    text: 'text-cyan-600',
    gradient: 'from-cyan-500 to-teal-600'
  },
  red: {
    bg: 'bg-red-500',
    bgLight: 'bg-red-500/10',
    text: 'text-red-600',
    gradient: 'from-red-500 to-rose-600'
  }
};

export const SquareKPICard = ({ 
  label, 
  value, 
  change, 
  isPositive = true, 
  icon: Icon, 
  color = 'blue',
  className = '' 
}) => {
  const theme = COLOR_THEMES[color] || COLOR_THEMES.blue;
  
  return (
    <div className={`relative overflow-hidden rounded-xl p-4 bg-white border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200 ${className}`}>
      {/* Gradient accent bar at top */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${theme.gradient}`} />
      
      <div className="flex flex-col h-full">
        {/* Icon and Label Row */}
        <div className="flex items-center justify-between mb-3">
          <div className={`w-10 h-10 rounded-lg ${theme.bgLight} flex items-center justify-center`}>
            {Icon && <Icon className={`w-5 h-5 ${theme.text}`} />}
          </div>
          {change && (
            <div className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${
              isPositive ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'
            }`}>
              {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {change}
            </div>
          )}
        </div>
        
        {/* Value */}
        <div className={`text-2xl font-bold ${theme.text} mb-1`}>
          {value}
        </div>
        
        {/* Label */}
        <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">
          {label}
        </div>
      </div>
    </div>
  );
};

/**
 * KPI Grid Container
 * Responsive grid for KPI cards - 4 columns on large screens, 2 on medium, 1 on small
 */
export const KPIGrid = ({ children, columns = 4, className = '' }) => {
  const gridCols = {
    2: 'grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-2 sm:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-5',
    6: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-6'
  };
  
  return (
    <div className={`grid ${gridCols[columns] || gridCols[4]} gap-4 ${className}`}>
      {children}
    </div>
  );
};

/**
 * Compact Stat Card - Even smaller for dense dashboards
 */
export const CompactStatCard = ({ 
  label, 
  value, 
  icon: Icon, 
  color = 'blue' 
}) => {
  const theme = COLOR_THEMES[color] || COLOR_THEMES.blue;
  
  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg ${theme.bgLight} border border-gray-100`}>
      <div className={`w-8 h-8 rounded-md ${theme.bg} flex items-center justify-center`}>
        {Icon && <Icon className="w-4 h-4 text-white" />}
      </div>
      <div>
        <div className={`text-lg font-bold ${theme.text}`}>{value}</div>
        <div className="text-xs text-gray-500">{label}</div>
      </div>
    </div>
  );
};

/**
 * Large Feature KPI Card - For hero metrics
 */
export const FeatureKPICard = ({ 
  label, 
  value, 
  subtitle,
  icon: Icon, 
  color = 'blue',
  className = '' 
}) => {
  const theme = COLOR_THEMES[color] || COLOR_THEMES.blue;
  
  return (
    <div className={`relative overflow-hidden rounded-2xl p-6 bg-gradient-to-br ${theme.gradient} text-white ${className}`}>
      {/* Background pattern */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
      
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          {Icon && (
            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
              <Icon className="w-6 h-6" />
            </div>
          )}
          <div className="text-sm font-medium opacity-90 uppercase tracking-wide">{label}</div>
        </div>
        
        <div className="text-4xl font-bold mb-1">{value}</div>
        {subtitle && <div className="text-sm opacity-80">{subtitle}</div>}
      </div>
    </div>
  );
};

export default SquareKPICard;
