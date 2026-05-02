import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { DEPARTMENT_ICONS, UI_ICONS } from '../data/departmentIcons';
import { useAuthStore } from '../stores/authStore';
import { 
  DataSourceBadge, 
  AutomationBadge, 
  ProblemResolutionCard, 
  AIImpactSummary,
  EnhancedKPICard 
} from '../components/InvestorDashboard';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * InvestorExecutiveDashboard - Investor-Ready Executive Command Center
 * Shows data provenance, automation metrics, and problem resolution visibility
 */
const InvestorExecutiveDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Demo data for investor presentation
  const [investorMetrics] = useState({
    problemsResolved: 47,
    automationRate: 92,
    humanIntervention: 8,
    dataPointsProcessed: 12847,
    avgResolutionTime: '4.2 min',
    manualTime: '45 min',
    platforms: {
      URGAA: { dataPoints: 7234, problems: 23, automated: 21 },
      GSTSAAS: { dataPoints: 4126, problems: 18, automated: 17 },
      IGNITION: { dataPoints: 1487, problems: 6, automated: 5 }
    }
  });

  const [problemsResolved] = useState([
    {
      problem: "Station #URG-047 offline for 2+ hours",
      solution: "Auto-triggered remote restart via OCPP, verified operational in 3 min",
      source: "URGAA",
      type: "external",
      automated: true,
      timestamp: "14:32",
      savings: "Saved 2h manual dispatch"
    },
    {
      problem: "Payment processing delay in 15 sessions",
      solution: "Switched to backup payment gateway, cleared queue automatically",
      source: "URGAA",
      type: "internal",
      automated: true,
      timestamp: "11:15",
      savings: "Revenue protected: ₹12,450"
    },
    {
      problem: "GST filing deadline for 12 workshops",
      solution: "Auto-generated returns, sent reminders, 10/12 submitted on time",
      source: "GSTSAAS",
      type: "external",
      automated: true,
      timestamp: "09:00",
      savings: "Avoided penalties: ₹24,000"
    },
    {
      problem: "Driver app crash reports increased 40%",
      solution: "Identified memory leak pattern, pushed hotfix via OTA update",
      source: "IGNITION",
      type: "internal",
      automated: true,
      timestamp: "16:45",
      savings: "User retention protected"
    }
  ]);

  const [shivData] = useState({
    mode: 'Meditation',
    threatsToday: 0,
    lastIntervention: 'Never',
    systemHealth: 98,
    autoResolved: 12,
    layers: [
      { name: 'Authentication', status: 'Active', source: 'URGAA' },
      { name: 'API Health', status: 'Active', source: 'ALL' },
      { name: 'System Load', status: 'Active', source: 'INTERNAL' },
      { name: 'Data Integrity', status: 'Active', source: 'GSTSAAS' },
      { name: 'Network Security', status: 'Active', source: 'INTERNAL' }
    ],
    recentActions: [
      { action: 'Suspicious login blocked', time: '14:32', source: 'URGAA', automated: true },
      { action: 'API rate limit auto-scaled', time: '09:15', source: 'INTERNAL', automated: true }
    ]
  });

  const [parvatiData] = useState({
    harmonyScore: 92,
    trend: 'improving',
    dimensions: [
      { name: 'Task Distribution', score: 90 },
      { name: 'Agent Utilization', score: 88 },
      { name: 'Response Time', score: 92 },
      { name: 'Completion Rate', score: 95 },
      { name: 'Conflict Resolution', score: 87 }
    ],
    optimizations: [
      { action: 'Rebalanced VISHWAKARMA → VAYU', tasks: 3, time: '2h ago', automated: true },
      { action: 'Prioritized stale tasks in LAKSHMI', tasks: 5, time: '4h ago', automated: true }
    ]
  });

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/dashboard/executive`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const data = await response.json();
      setDashboardData(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderIcon = (svgString) => (
    <span dangerouslySetInnerHTML={{ __html: svgString }} />
  );

  if (loading && !dashboardData) {
    return (
      <div className="min-h-screen bg-dark-slate flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-g4g-electric-yellow border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-cool-grey">Loading Executive Dashboard...</p>
        </div>
      </div>
    );
  }

  const { kpis, departments } = dashboardData || {};

  return (
    <div className="min-h-screen bg-dark-slate">
      {/* Header */}
      <header className="bg-g4g-blue border-b border-g4g-steel-grey px-6 py-4 sticky top-0 z-50">
        <div className="flex items-center justify-between max-w-[1920px] mx-auto">
          {/* Left - Logo & Title */}
          <div className="flex items-center gap-4">
            <Link to="/kailash" className="text-cool-grey hover:text-white transition-colors">
              <span dangerouslySetInnerHTML={{ __html: UI_ICONS.ARROW_LEFT }} />
            </Link>
            <div>
              <h1 className="text-xl font-black text-white tracking-tight">Kailash</h1>
              <p className="text-xs text-cool-grey">Executive Command Center — Go4Garage</p>
            </div>
          </div>

          {/* Center - Live Status */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <span className="w-2 h-2 bg-highlight-teal rounded-full animate-pulse" />
              <span className="text-highlight-teal font-medium">Data Sync: Live</span>
            </div>
            <span className="text-cool-grey text-xs">
              Last Updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Loading...'}
            </span>
            <span className="text-cool-grey text-xs px-2 py-1 bg-g4g-graphite rounded">v2.1.0</span>
          </div>

          {/* Right - Actions */}
          <div className="flex items-center gap-3">
            <button 
              onClick={fetchDashboardData}
              className="px-4 py-2 bg-g4g-graphite text-cool-grey text-sm font-medium rounded-lg hover:text-white transition-colors flex items-center gap-2"
            >
              <span dangerouslySetInnerHTML={{ __html: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/><path d="M12 6v6l4 2"/></svg>` }} />
              Refresh
            </button>
            <button 
              onClick={() => navigate('/ganesha-chat')}
              className="px-5 py-2 bg-g4g-electric-yellow text-dark-slate text-sm font-bold rounded-lg hover:bg-yellow-400 transition-colors"
            >
              GANESHA AI
            </button>
            
            {/* User Menu */}
            <div className="relative">
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 px-3 py-2 bg-g4g-graphite rounded-lg hover:bg-g4g-steel-grey transition-colors"
              >
                <div className="w-8 h-8 bg-g4g-electric-yellow/20 rounded-full flex items-center justify-center">
                  <span className="text-g4g-electric-yellow font-bold text-sm">
                    {user?.full_name?.charAt(0) || 'U'}
                  </span>
                </div>
                <span className="text-white text-sm font-medium hidden sm:inline">
                  {user?.full_name || 'User'}
                </span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-cool-grey">
                  <path d="M6 9l6 6 6-6"/>
                </svg>
              </button>
              
              {showUserMenu && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-g4g-graphite rounded-xl border border-g4g-steel-grey shadow-2xl z-50 overflow-hidden">
                  <div className="p-4 border-b border-g4g-steel-grey">
                    <p className="text-white font-semibold">{user?.full_name || 'User'}</p>
                    <p className="text-xs text-cool-grey">{user?.email || 'user@kailash.ai'}</p>
                    <p className="text-xs text-g4g-electric-yellow mt-1">Kailash: {user?.kailash_code || '<REDACTED_kailash_code>'}</p>
                  </div>
                  <div className="p-2">
                    <button 
                      onClick={() => { navigate('/settings'); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-3 px-3 py-2 text-cool-grey hover:text-white hover:bg-g4g-steel-grey/50 rounded-lg transition-colors text-sm"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="3"/>
                        <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
                      </svg>
                      Settings
                    </button>
                    <button 
                      onClick={() => { navigate('/analytics'); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-3 px-3 py-2 text-cool-grey hover:text-white hover:bg-g4g-steel-grey/50 rounded-lg transition-colors text-sm"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M18 20V10"/>
                        <path d="M12 20V4"/>
                        <path d="M6 20v-6"/>
                      </svg>
                      Analytics
                    </button>
                    <div className="border-t border-g4g-steel-grey my-2"></div>
                    <button 
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-3 py-2 text-error-red hover:bg-error-red/10 rounded-lg transition-colors text-sm"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
                        <polyline points="16 17 21 12 16 7"/>
                        <line x1="21" y1="12" x2="9" y2="12"/>
                      </svg>
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-[1920px] mx-auto p-6">
        {/* AI IMPACT SUMMARY - TOP PRIORITY FOR INVESTORS */}
        <AIImpactSummary metrics={investorMetrics} />

        {/* GUARDIAN PANELS */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* SHIV GUARDIAN */}
          <div className="bg-g4g-graphite rounded-xl p-6 border border-g4g-steel-grey hover:border-g4g-electric-yellow/30 transition-all">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-g4g-blue/20 rounded-xl">
                  <span className="text-g4g-blue" dangerouslySetInnerHTML={{ __html: UI_ICONS.SHIELD }} />
                </div>
                <div>
                  <h2 className="text-xl font-black text-g4g-electric-yellow">SHIV GUARDIAN</h2>
                  <p className="text-sm text-cool-grey">Security & System Monitoring</p>
                </div>
              </div>
              <span className="px-3 py-1.5 bg-highlight-teal/20 text-highlight-teal text-xs font-bold rounded-full uppercase">
                {shivData.mode}
              </span>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-dark-slate rounded-lg p-4 text-center">
                <div className="text-3xl font-black text-g4g-electric-yellow">{shivData.threatsToday}</div>
                <div className="text-xs text-cool-grey mt-1">Threats Today</div>
              </div>
              <div className="bg-dark-slate rounded-lg p-4 text-center">
                <div className="text-3xl font-black text-highlight-teal">{shivData.autoResolved}</div>
                <div className="text-xs text-cool-grey mt-1">Auto-Resolved</div>
              </div>
              <div className="bg-dark-slate rounded-lg p-4 text-center">
                <div className="text-3xl font-black text-g4g-electric-yellow">{shivData.systemHealth}%</div>
                <div className="text-xs text-cool-grey mt-1">System Health</div>
              </div>
            </div>

            {/* Monitoring Layers */}
            <div className="border-t border-g4g-steel-grey pt-4 mb-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wide mb-3">Monitoring Layers</h3>
              <div className="space-y-2">
                {shivData.layers.map((layer, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-highlight-teal/10 rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className="text-highlight-teal" dangerouslySetInnerHTML={{ __html: UI_ICONS.CHECK }} />
                      <span className="text-sm text-white">{layer.name}</span>
                    </div>
                    <DataSourceBadge source={layer.source} />
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Auto-Resolved */}
            <div className="border-t border-g4g-steel-grey pt-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wide mb-3">Problems Resolved by SHIV</h3>
              <div className="space-y-2">
                {shivData.recentActions.map((action, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-dark-slate rounded-lg">
                    <span className="text-sm text-white">{action.action}</span>
                    <div className="flex items-center gap-2">
                      <DataSourceBadge source={action.source} timestamp={action.time} />
                      <AutomationBadge automated={action.automated} showLabel={false} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* PARVATI HARMONY */}
          <div className="bg-g4g-graphite rounded-xl p-6 border border-g4g-steel-grey hover:border-g4g-electric-yellow/30 transition-all">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-pink-500/20 rounded-xl">
                  <span className="text-pink-500" dangerouslySetInnerHTML={{ __html: UI_ICONS.BALANCE }} />
                </div>
                <div>
                  <h2 className="text-xl font-black text-g4g-electric-yellow">PARVATI HARMONY</h2>
                  <p className="text-sm text-cool-grey">Workload Balance & Optimization</p>
                </div>
              </div>
            </div>

            {/* Harmony Score */}
            <div className="text-center p-6 bg-highlight-teal/10 rounded-xl mb-6">
              <div className="text-6xl font-black text-g4g-electric-yellow mb-2">{parvatiData.harmonyScore}</div>
              <div className="text-sm text-cool-grey mb-2">Harmony Score / 100</div>
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-highlight-teal/20 text-highlight-teal text-xs font-bold rounded-full">
                {parvatiData.trend} ↑
              </span>
            </div>

            {/* Dimensions */}
            <div className="space-y-3 mb-4">
              {parvatiData.dimensions.map((dim, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-cool-grey">{dim.name}</span>
                    <span className="font-bold text-white">{dim.score}%</span>
                  </div>
                  <div className="h-2 bg-dark-slate rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-pink-500 to-purple-600 rounded-full transition-all"
                      style={{ width: `${dim.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* AI Optimizations */}
            <div className="border-t border-g4g-steel-grey pt-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wide mb-3">AI Optimizations Today</h3>
              <div className="space-y-2">
                {parvatiData.optimizations.map((opt, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-dark-slate rounded-lg">
                    <div>
                      <span className="text-sm text-white">{opt.action}</span>
                      <span className="text-xs text-cool-grey ml-2">{opt.tasks} tasks</span>
                    </div>
                    <AutomationBadge automated={opt.automated} showLabel={false} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* KPI CARDS WITH DATA PROVENANCE */}
        <div className="mb-8">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-g4g-electric-yellow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 3v18h18"/>
                <path d="M18 17V9"/>
                <path d="M13 17V5"/>
                <path d="M8 17v-3"/>
              </svg>
            </span>
            Key Performance Indicators
          </h2>
          <div className="grid grid-cols-6 gap-4">
            <EnhancedKPICard 
              title="Company Health"
              value={`${kpis?.company_health?.value || 85}%`}
              source="INTERNAL"
              type="internal"
              timestamp="2m ago"
              trend="+5%"
              trendDirection="up"
              aiCalculated={true}
            />
            <EnhancedKPICard 
              title="Total Revenue"
              value={`₹${((kpis?.total_revenue?.value || 4250000) / 100000).toFixed(1)}L`}
              source="URGAA"
              type="external"
              timestamp="Live"
              trend="+12%"
              trendDirection="up"
              aiCalculated={true}
            />
            <EnhancedKPICard 
              title="Active Users"
              value={(kpis?.active_users?.value || 15234).toLocaleString()}
              source="IGNITION"
              type="external"
              timestamp="5m ago"
              trend="+8%"
              trendDirection="up"
            />
            <EnhancedKPICard 
              title="System Uptime"
              value={`${kpis?.system_uptime?.value || 99.7}%`}
              source="INTERNAL"
              type="internal"
              timestamp="Live"
              trend="→0%"
              trendDirection="neutral"
            />
            <EnhancedKPICard 
              title="Auto-Resolved"
              value={`${kpis?.auto_resolved?.value || 75}%`}
              source="ALL"
              type="internal"
              timestamp="Today"
              trend="+3%"
              trendDirection="up"
              description="No human needed"
            />
            <EnhancedKPICard 
              title="Alerts Today"
              value={kpis?.alerts_today?.value || 3}
              source="INTERNAL"
              type="internal"
              timestamp="Live"
              trend="-2"
              trendDirection="down"
            />
          </div>
        </div>

        {/* PROBLEMS RESOLVED SHOWCASE */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span className="text-g4g-electric-yellow">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M9 12l2 2 4-4"/>
                </svg>
              </span>
              Problems Resolved Today
            </h2>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-white font-semibold">{problemsResolved.length} resolved</span>
              <span className="text-cool-grey">|</span>
              <span className="text-highlight-teal font-semibold">92% automated</span>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            {problemsResolved.map((problem, idx) => (
              <ProblemResolutionCard key={idx} {...problem} />
            ))}
          </div>
        </div>

        {/* DATA SOURCES SECTION */}
        <div className="mb-8">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-g4g-electric-yellow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <ellipse cx="12" cy="5" rx="9" ry="3"/>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
              </svg>
            </span>
            Data Intelligence Summary
          </h2>
          
          <div className="grid grid-cols-2 gap-6">
            {/* Internal Data */}
            <div className="bg-g4g-graphite rounded-xl p-5 border border-g4g-steel-grey">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full" />
                INTERNAL DATA (Company Operations)
              </h3>
              <div className="space-y-3">
                {[
                  { source: 'MongoDB', type: 'Database', status: 'Live', sync: 'Real-time' },
                  { source: 'API Gateway', type: 'Metrics', status: 'Live', sync: 'Real-time' },
                  { source: 'Auth Service', type: 'Sessions', status: 'Live', sync: '5 min' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-dark-slate rounded-lg">
                    <div>
                      <span className="text-white text-sm font-medium">{item.source}</span>
                      <span className="text-cool-grey text-xs ml-2">({item.type})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-highlight-teal rounded-full animate-pulse" />
                      <span className="text-xs text-cool-grey">{item.sync}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* External Data */}
            <div className="bg-g4g-graphite rounded-xl p-5 border border-g4g-steel-grey">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-emerald-500 rounded-full" />
                EXTERNAL DATA (Product Intelligence)
              </h3>
              <div className="space-y-3">
                {[
                  { source: 'URGAA', type: 'EV Charging', status: 'Live', sync: 'Real-time', product: 'URGAA' },
                  { source: 'GSTSAAS', type: 'Workshop Mgmt', status: 'Live', sync: '15 min', product: 'GSTSAAS' },
                  { source: 'IGNITION', type: 'Mobile App', status: 'Live', sync: '5 min', product: 'IGNITION' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-dark-slate rounded-lg">
                    <div className="flex items-center gap-2">
                      <DataSourceBadge source={item.product} />
                      <span className="text-white text-sm font-medium">{item.source}</span>
                      <span className="text-cool-grey text-xs">({item.type})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-highlight-teal rounded-full animate-pulse" />
                      <span className="text-xs text-cool-grey">{item.sync}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* DEPARTMENT QUICK ACCESS */}
        <div className="mb-8">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-g4g-electric-yellow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7"/>
                <rect x="14" y="3" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/>
              </svg>
            </span>
            Department Quick Access
          </h2>

          <div className="grid grid-cols-2 gap-6">
            {/* Internal Departments */}
            <div className="bg-g4g-graphite rounded-xl p-5 border border-g4g-steel-grey">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full" />
                Internal Departments (15)
              </h3>
              <div className="flex flex-wrap gap-2">
                {[
                  { name: 'GANESHA', role: 'Executive AI' },
                  { name: 'VISHWAKARMA', role: 'Technology/CTO' },
                  { name: 'LAKSHMI', role: 'Finance/CFO' },
                  { name: 'KUBERA', role: 'Sales/CSO' },
                  { name: 'KAMADEVA', role: 'Marketing/CMO' },
                  { name: 'BRIHASPATI', role: 'Investor Relations' },
                  { name: 'MITRA', role: 'Partnerships' },
                  { name: 'DHARMA', role: 'Government' },
                  { name: 'SHUKRA', role: 'Strategy/CSO' },
                  { name: 'CHANDRA', role: 'Data & Analytics' },
                  { name: 'INDRA', role: 'Operations/COO' },
                  { name: 'CHITRAGUPTA', role: 'Quality Assurance' },
                  { name: 'PRAJAPATI', role: 'Product Mgmt' },
                  { name: 'YAMA', role: 'Legal & Compliance' },
                  { name: 'VAYU', role: 'Sustainability/ESG' }
                ].map((dept, idx) => (
                  <Link 
                    key={idx}
                    to={`/department/${dept.name.toLowerCase()}`}
                    className="px-3 py-2 bg-dark-slate text-white text-xs font-medium rounded-lg hover:bg-indigo-500/20 hover:text-indigo-400 transition-all border border-transparent hover:border-indigo-500/50 group"
                    title={dept.role}
                  >
                    {dept.name}
                  </Link>
                ))}
              </div>
            </div>

            {/* External Departments */}
            <div className="bg-g4g-graphite rounded-xl p-5 border border-g4g-steel-grey">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-emerald-500 rounded-full" />
                External Departments (3) — Product Intelligence
              </h3>
              <div className="flex flex-wrap gap-3">
                {[
                  { name: 'SURYA', product: 'URGAA', color: 'bg-amber-500/20 text-amber-400 border-amber-500/50' },
                  { name: 'TVASHTA', product: 'GSTSAAS', color: 'bg-purple-500/20 text-purple-400 border-purple-500/50' },
                  { name: 'KARTIKEYA', product: 'IGNITION', color: 'bg-pink-500/20 text-pink-400 border-pink-500/50' }
                ].map((dept, idx) => (
                  <Link 
                    key={idx}
                    to={`/department/${dept.name.toLowerCase()}`}
                    className={`px-4 py-3 rounded-lg transition-all border ${dept.color} hover:scale-105 flex flex-col items-center min-w-[120px]`}
                  >
                    <span className="font-bold">{dept.name}</span>
                    <span className="text-[10px] opacity-80">{dept.product}</span>
                  </Link>
                ))}
              </div>
              
              <div className="mt-4 p-3 bg-dark-slate rounded-lg">
                <p className="text-xs text-cool-grey">
                  <span className="text-highlight-teal font-semibold">External departments</span> process data from Go4Garage&apos;s 
                  product ecosystem: URGAA (EV Charging), GSTSAAS (Workshop Management), and IGNITION (Mobile App).
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default InvestorExecutiveDashboard;
